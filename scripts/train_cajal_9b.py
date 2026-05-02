#!/usr/bin/env python3
"""
CAJAL-9B Training Script
Train Qwen3.5-9B with LoRA on the agent workflow dataset.
Optimized for Windows + RTX 3090 24GB.

Usage:
    python scripts/train_cajal_9b.py
    or
    train_9b.bat
"""

import sys
import io
import json
import os
import time
import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig,
    DataCollatorForSeq2Seq,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# Configuration
MODEL_PATH = r"D:\PROJECTS\CAJAL\Modelos_originales\Qwen3.5-9B"
DATASET_PATH = r"D:\PROJECTS\CAJAL\datasets\cajal_9b_mega_dataset.jsonl"
SYSTEM_PROMPT_PATH = r"D:\PROJECTS\CAJAL\cajal_9b_system_prompt.txt"
OUTPUT_DIR = r"D:\PROJECTS\CAJAL\outputs\CAJAL-9B"
CHECKPOINT_DIR = os.path.join(OUTPUT_DIR, "checkpoints")
ADAPTER_DIR = os.path.join(OUTPUT_DIR, "CAJAL-9B-lora")
MERGED_DIR = os.path.join(OUTPUT_DIR, "CAJAL-9B-merged-16bit")
LOG_FILE = os.path.join(OUTPUT_DIR, f"training_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Training hyperparameters
EPOCHS = 5
BATCH_SIZE = 1
GRAD_ACCUMULATION = 4
LEARNING_RATE = 1e-4
LORA_R = 32
LORA_ALPHA = 64
LORA_DROPOUT = 0.05
MAX_SEQ_LENGTH = 4096
WARMUP_RATIO = 0.1
WEIGHT_DECAY = 0.01
SAVE_STEPS = 50
LOGGING_STEPS = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def format_chat_example(example, tokenizer, system_prompt):
    """Format a conversation example for training."""
    messages = example.get("messages", [])
    if not messages:
        return ""
    
    # Ensure system prompt is present
    has_system = any(m.get("role") == "system" for m in messages)
    if not has_system:
        messages = [{"role": "system", "content": system_prompt}] + messages
    else:
        # Replace system prompt with ours
        for m in messages:
            if m.get("role") == "system":
                m["content"] = system_prompt
    
    try:
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        return text
    except Exception as e:
        log(f"Warning: Chat template failed: {e}")
        # Fallback manual formatting
        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                parts.append(f"<|im_start|>system\n{content}<|im_end|>")
            elif role == "user":
                parts.append(f"<|im_start|>user\n{content}<|im_end|>")
            elif role == "assistant":
                parts.append(f"<|im_start|>assistant\n{content}<|im_end|>")
        return "\n".join(parts)

def load_dataset(tokenizer, system_prompt):
    """Load and format the training dataset."""
    log(f"Loading dataset from: {DATASET_PATH}")
    
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        raw_data = [json.loads(line) for line in f if line.strip()]
    
    log(f"Loaded {len(raw_data)} examples")
    
    formatted = []
    for i, ex in enumerate(raw_data):
        text = format_chat_example(ex, tokenizer, system_prompt)
        if text:
            formatted.append({"text": text})
        if (i + 1) % 10 == 0:
            log(f"Formatted {i+1}/{len(raw_data)} examples")
    
    log(f"Total formatted examples: {len(formatted)}")
    
    # Log a sample
    if formatted:
        sample_len = len(formatted[0]["text"])
        log(f"Sample text length: {sample_len} chars")
        log(f"Sample preview:\n{formatted[0]['text'][:500]}...")
    
    return Dataset.from_list(formatted)

def main():
    log("=" * 60)
    log("CAJAL-9B Training Started")
    log("=" * 60)
    log(f"PyTorch version: {torch.__version__}")
    log(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        log(f"CUDA device: {torch.cuda.get_device_name(0)}")
        log(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    # Load system prompt
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        system_prompt = f.read().strip()
    log(f"System prompt loaded: {len(system_prompt)} chars")
    
    # Load tokenizer
    log("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        padding_side="right",
    )
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    log(f"Tokenizer vocab size: {len(tokenizer)}")
    
    # Quantization config
    log("Setting up 4-bit quantization...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    
    # Load model
    log("Loading Qwen3.5-9B model (this will take ~5 minutes)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2" if torch.cuda.get_device_capability()[0] >= 8 else "eager",
    )
    log(f"Model loaded: {type(model).__name__}")
    log(f"Model device map: {model.hf_device_map if hasattr(model, 'hf_device_map') else 'auto'}")
    
    # Prepare model for k-bit training
    log("Preparing model for QLoRA training...")
    model = prepare_model_for_kbit_training(model)
    
    # LoRA config
    log(f"Applying LoRA (r={LORA_R}, alpha={LORA_ALPHA}, dropout={LORA_DROPOUT})...")
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        use_rslora=True,  # Rank-stabilized LoRA for larger models
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    log(f"Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    
    # Load dataset
    dataset = load_dataset(tokenizer, system_prompt)
    
    # Training arguments
    log("Configuring training...")
    training_args = TrainingArguments(
        output_dir=CHECKPOINT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUMULATION,
        optim="paged_adamw_8bit",
        learning_rate=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
        warmup_ratio=WARMUP_RATIO,
        lr_scheduler_type="cosine",
        logging_steps=LOGGING_STEPS,
        save_steps=SAVE_STEPS,
        save_total_limit=3,
        max_grad_norm=0.3,
        fp16=False,
        bf16=torch.cuda.is_bf16_supported(),
        group_by_length=True,
        report_to="none",
        remove_unused_columns=False,
        seed=42,
    )
    
    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        label_pad_token_id=-100,
        padding=True,
    )
    
    # Trainer
    log("Initializing SFTTrainer...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        args=training_args,
        data_collator=data_collator,
        max_seq_length=MAX_SEQ_LENGTH,
        dataset_text_field="text",
        tokenizer=tokenizer,
    )
    
    # Train
    log("=" * 60)
    log("Starting training...")
    log(f"Epochs: {EPOCHS}, Batch size: {BATCH_SIZE}, Grad accum: {GRAD_ACCUMULATION}")
    log(f"Effective batch size: {BATCH_SIZE * GRAD_ACCUMULATION}")
    log(f"Learning rate: {LEARNING_RATE}")
    log(f"Max sequence length: {MAX_SEQ_LENGTH}")
    log("=" * 60)
    
    start_time = time.time()
    trainer.train()
    elapsed = time.time() - start_time
    
    log("=" * 60)
    log(f"Training complete! Time: {elapsed/60:.1f} minutes")
    log("=" * 60)
    
    # Save adapters
    log(f"Saving LoRA adapters to: {ADAPTER_DIR}")
    model.save_pretrained(ADAPTER_DIR)
    tokenizer.save_pretrained(ADAPTER_DIR)
    
    # Save training info
    info = {
        "model_name": "CAJAL-9B",
        "base_model": "Qwen3.5-9B",
        "training_date": datetime.datetime.now().isoformat(),
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
        "gradient_accumulation": GRAD_ACCUMULATION,
        "learning_rate": LEARNING_RATE,
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "lora_dropout": LORA_DROPOUT,
        "max_seq_length": MAX_SEQ_LENGTH,
        "dataset_size": len(dataset),
        "training_time_minutes": elapsed / 60,
        "system_prompt_length": len(system_prompt),
        "hardware": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
    }
    with open(os.path.join(ADAPTER_DIR, "training_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    log("Training info saved")
    
    # Save system prompt
    with open(os.path.join(ADAPTER_DIR, "system_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(system_prompt)
    log("System prompt saved")
    
    log("=" * 60)
    log("CAJAL-9B LoRA adapters saved successfully!")
    log(f"Location: {ADAPTER_DIR}")
    log("Next steps:")
    log("  1. Merge adapters: python merge_and_test.py --model 9b")
    log("  2. Convert to GGUF: python convert_hf_to_gguf.py")
    log("  3. Create Ollama model: ollama create cajal-9b -f Modelfile")
    log("=" * 60)

if __name__ == "__main__":
    main()
