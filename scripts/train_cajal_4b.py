#!/usr/bin/env python3
"""
CAJAL-4B Fine-Tuning Script
Train Qwen3.5-4B on P2PCLAW scientific papers dataset.
Runs on Windows without Unsloth (transformers + bitsandbytes + PEFT).

Usage:
    python train_cajal_4b.py --dataset cajal_dataset.jsonl
"""

import argparse
import gc
import json
import logging
import os
import sys
import time
import traceback
from typing import Any, Dict, List

import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CAJAL|%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("training_4B.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("CAJAL")

SYSTEM_PROMPT = (
    "You are CAJAL, an AI scientist in the P2PCLAW decentralized "
    "research network. You write rigorous, reproducible academic papers "
    "with structured methodology, statistical analysis, Lean 4 proofs, "
    "and proper citations. Always reason step-by-step and ground "
    "claims in evidence. /think"
)


def parse_args():
    parser = argparse.ArgumentParser(description="CAJAL-4B Training")
    parser.add_argument("--model-path", default=r"D:\PROJECTS\CAJAL\Modelos_originales\Qwen3.5-4B")
    parser.add_argument("--dataset", required=True, help="Path to JSONL dataset")
    parser.add_argument("--output-dir", default="./outputs/CAJAL-4B")
    parser.add_argument("--output-name", default="CAJAL-4B")
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--warmup-steps", type=int, default=100)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=3407)
    parser.add_argument("--use-thinking", action="store_true", default=True)
    parser.add_argument("--export-gguf", action="store_true")
    parser.add_argument("--gguf-quant", default="q4_k_m")
    parser.add_argument("--resume-from-checkpoint", default=None, help="Resume training from checkpoint directory")
    return parser.parse_args()


def load_jsonl_dataset(path: str) -> Dataset:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    logger.info(f"Loading dataset from {path}")
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning(f"Skipping invalid JSON on line {line_num}: {e}")
                continue

            if isinstance(obj, list) and all(isinstance(m, dict) for m in obj):
                messages = obj
            elif isinstance(obj, dict) and "messages" in obj:
                messages = obj["messages"]
            elif isinstance(obj, dict) and "conversations" in obj:
                messages = obj["conversations"]
            elif isinstance(obj, dict) and "instruction" in obj:
                messages = [
                    {"role": "user", "content": obj["instruction"]},
                    {"role": "assistant", "content": obj.get("output", obj.get("response", ""))},
                ]
            else:
                continue

            data.append({"messages": messages})

    logger.info(f"Loaded {len(data)} conversations")
    return Dataset.from_list(data)


def main():
    args = parse_args()

    logger.info("=" * 60)
    logger.info("CAJAL-4B Fine-Tuning")
    logger.info("=" * 60)
    logger.info(f"Model: {args.model_path}")
    logger.info(f"Dataset: {args.dataset}")
    logger.info(f"Output: {args.output_name}")
    logger.info(f"LoRA r={args.lora_r}, alpha={args.lora_alpha}")
    logger.info(f"Epochs={args.epochs}, batch={args.batch_size}, grad_accum={args.grad_accum}")
    logger.info(f"Learning rate={args.lr}, max_seq_length={args.max_seq_length}")
    logger.info(f"CUDA: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    os.makedirs(args.output_dir, exist_ok=True)

    # 1. Load tokenizer
    logger.info("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 2. Load model with 4-bit quantization
    logger.info("Loading model in 4-bit (QLoRA)...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        attn_implementation="eager",  # Use eager instead of flash_attention for compatibility
    )

    logger.info(f"Model loaded: {type(model).__name__}")
    vram = torch.cuda.memory_allocated(0) / 1e9 if torch.cuda.is_available() else 0
    logger.info(f"VRAM after model load: {vram:.2f} GB")

    # 3. Prepare model for k-bit training and add LoRA
    logger.info("Preparing model for training...")
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    vram = torch.cuda.memory_allocated(0) / 1e9 if torch.cuda.is_available() else 0
    logger.info(f"VRAM after LoRA: {vram:.2f} GB")

    # 4. Load and format dataset
    train_dataset = load_jsonl_dataset(args.dataset)
    if len(train_dataset) == 0:
        logger.error("Dataset is empty!")
        return 1

    def format_conversations(examples):
        texts = []
        for messages in examples["messages"]:
            formatted = []
            for msg in messages:
                role = msg.get("role", msg.get("from", "user"))
                content = msg.get("content", msg.get("value", msg.get("text", "")))
                if role in ("human", "user"):
                    role = "user"
                elif role in ("gpt", "assistant", "model"):
                    role = "assistant"
                formatted.append({"role": role, "content": content})

            if formatted and formatted[0].get("role") != "system":
                formatted.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

            if args.use_thinking and not formatted[0]["content"].endswith("/think"):
                formatted[0]["content"] += " /think"

            try:
                text = tokenizer.apply_chat_template(
                    formatted,
                    tokenize=False,
                    add_generation_prompt=False,
                )
            except Exception:
                text = "\n\n".join(f"{m['role']}: {m['content']}" for m in formatted)

            texts.append(text)
        return {"text": texts}

    train_dataset = train_dataset.map(
        format_conversations,
        batched=True,
        desc="Applying chat template",
    )

    # 5. Create trainer
    effective_batch = args.batch_size * args.grad_accum
    logger.info(f"Effective batch size: {effective_batch}")

    training_args = SFTConfig(
        output_dir=os.path.join(args.output_dir, "checkpoints"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        warmup_steps=args.warmup_steps,
        weight_decay=args.weight_decay,
        lr_scheduler_type="cosine",
        max_grad_norm=0.3,
        logging_steps=10,
        save_strategy="epoch",
        save_total_limit=2,
        seed=args.seed,
        bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
        fp16=not (torch.cuda.is_available() and torch.cuda.is_bf16_supported()),
        optim="adamw_8bit",
        report_to=["none"],
        gradient_checkpointing=True,
        dataset_num_proc=2,
        remove_unused_columns=False,
        dataloader_num_workers=0,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        processing_class=tokenizer,
        args=training_args,
        formatting_func=lambda ex: ex["text"],
    )

    # 6. Train
    logger.info("=" * 60)
    logger.info("Starting training")
    logger.info("=" * 60)

    start_time = time.time()
    try:
        if args.resume_from_checkpoint and os.path.isdir(args.resume_from_checkpoint):
            logger.info(f"Resuming from checkpoint: {args.resume_from_checkpoint}")
            trainer.train(resume_from_checkpoint=args.resume_from_checkpoint)
        else:
            trainer.train()
    except torch.cuda.OutOfMemoryError:
        logger.error("OOM! Try reducing batch_size or max_seq_length")
        raise
    except Exception as e:
        logger.error(f"Training failed: {e}")
        traceback.print_exc()
        raise

    elapsed = time.time() - start_time
    logger.info(f"Training completed in {elapsed / 60:.1f} minutes")

    # 7. Save adapters
    adapters_dir = os.path.join(args.output_dir, f"{args.output_name}-lora")
    model.save_pretrained(adapters_dir)
    tokenizer.save_pretrained(adapters_dir)
    logger.info(f"LoRA adapters saved to {adapters_dir}")

    # Save training info
    info = {
        "model_name": args.output_name,
        "base_model": args.model_path,
        "adapter_format": "PEFT LoRA",
        "lora_r": args.lora_r,
        "lora_alpha": args.lora_alpha,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "grad_accum": args.grad_accum,
        "learning_rate": args.lr,
        "max_seq_length": args.max_seq_length,
        "training_time_minutes": round(elapsed / 60, 2),
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(os.path.join(adapters_dir, "training_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

    # 8. Quick evaluation
    logger.info("Running quick evaluation...")
    model.eval()
    test_prompt = "Explain the key differences between CRISPR-Cas9 and base editing in gene therapy."
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": test_prompt},
    ]
    inputs = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
    logger.info(f"Eval response: {response[:300]}...")

    logger.info("=" * 60)
    logger.info("CAJAL-4B training completed!")
    logger.info("=" * 60)

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return 0


if __name__ == "__main__":
    sys.exit(main())