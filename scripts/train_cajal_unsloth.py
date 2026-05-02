#!/usr/bin/env python3
"""
CAJAL Fine-Tuning Script - Unsloth Optimized
=============================================
Train CAJAL models on scientific papers using Unsloth + QLoRA/LoRA.

Designed to run in WSL2 or Docker with GPU access.
Supports: Qwen3.6-27B (CAJAL-27B), Qwen3.5-9B (CAJAL-9B), Qwen3.5-4B (CAJAL-4B)

Usage (WSL2 or Docker):
    python train_cajal_unsloth.py \
        --model qwen3.6-27b \
        --dataset /workspace/cajal_dataset.jsonl \
        --output-name CAJAL-27B
"""

import argparse
import gc
import json
import logging
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from datasets import Dataset, load_dataset
from trl import SFTTrainer, SFTConfig

from unsloth import FastLanguageModel

MODEL_CONFIGS = {
    "qwen3.6-27b": {
        "model_id": "Qwen/Qwen3.6-27B",
        "chat_template": "qwen3",
        "max_seq_length_default": 4096,
        "supports_thinking": True,
        "system_prompt": (
            "You are CAJAL, an AI scientist in the P2PCLAW decentralized "
            "research network. You write rigorous, reproducible academic papers "
            "with structured methodology, statistical analysis, Lean 4 proofs, "
            "and proper citations. Always reason step-by-step and ground "
            "claims in evidence. /think"
        ),
    },
    "qwen3.5-9b": {
        "model_id": "Qwen/Qwen3.5-9B",
        "chat_template": "qwen3",
        "max_seq_length_default": 8192,
        "supports_thinking": True,
        "system_prompt": (
            "You are CAJAL, an AI scientist in the P2PCLAW decentralized "
            "research network. You write rigorous, reproducible academic papers "
            "with structured methodology, statistical analysis, Lean 4 proofs, "
            "and proper citations. Always reason step-by-step and ground "
            "claims in evidence. /think"
        ),
    },
    "qwen3.5-4b": {
        "model_id": "Qwen/Qwen3.5-4B",
        "chat_template": "qwen3",
        "max_seq_length_default": 8192,
        "supports_thinking": True,
        "system_prompt": (
            "You are CAJAL, an AI scientist in the P2PCLAW decentralized "
            "research network. You write rigorous, reproducible academic papers "
            "with structured methodology, statistical analysis, Lean 4 proofs, "
            "and proper citations. Always reason step-by-step and ground "
            "claims in evidence. /think"
        ),
    },
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CAJAL|%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("cajal_training_unsloth.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("CAJAL")


def parse_args():
    parser = argparse.ArgumentParser(description="CAJAL Fine-Tuning with Unsloth")
    parser.add_argument("--model", default="qwen3.6-27b", choices=list(MODEL_CONFIGS.keys()))
    parser.add_argument("--dataset", required=True, help="Path to JSONL dataset")
    parser.add_argument("--local-model-path", default=None, help="Local path to model (overrides HuggingFace download)")
    parser.add_argument("--output-dir", default="./outputs")
    parser.add_argument("--output-name", default="CAJAL")
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=16)
    parser.add_argument("--lora-dropout", type=float, default=0.0)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=8)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--warmup-steps", type=int, default=100)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--max-grad-norm", type=float, default=0.3)
    parser.add_argument("--seed", type=int, default=3407)
    parser.add_argument("--load-in-4bit", action="store_true", default=True)
    parser.add_argument("--load-in-16bit", action="store_true")
    parser.add_argument("--use-thinking", action="store_true")
    parser.add_argument("--export-gguf", action="store_true")
    parser.add_argument("--gguf-quant", default="q4_k_m", choices=["q4_0", "q4_k_m", "q5_k_m", "q8_0", "f16"])
    parser.add_argument("--save-merged", action="store_true")
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
    config = MODEL_CONFIGS[args.model]
    model_name = args.local_model_path if args.local_model_path else config["model_id"]
    system_prompt = config["system_prompt"]

    logger.info("=" * 60)
    logger.info("CAJAL Fine-Tuning with Unsloth")
    logger.info("=" * 60)
    logger.info(f"Model: {model_name}")
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

    max_seq_length = args.max_seq_length
    if max_seq_length > config["max_seq_length_default"]:
        logger.warning(f"Clamping max_seq_length to {config['max_seq_length_default']}")
        max_seq_length = config["max_seq_length_default"]

    # 1. Load model with Unsloth
    logger.info("Loading model with Unsloth FastLanguageModel...")
    load_in_4bit = args.load_in_4bit and not args.load_in_16bit
    load_in_16bit = args.load_in_16bit

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit,
        load_in_16bit=load_in_16bit,
        full_finetuning=False,
        trust_remote_code=True,
    )

    logger.info("Model loaded successfully!")
    vram = torch.cuda.memory_allocated(0) / 1e9 if torch.cuda.is_available() else 0
    logger.info(f"VRAM after load: {vram:.1f} GB")

    # 2. Setup LoRA adapters
    logger.info(f"Configuring LoRA: r={args.lora_r}, alpha={args.lora_alpha}")

    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=args.seed,
        use_rslora=False,
    )

    logger.info("LoRA adapters attached")
    vram = torch.cuda.memory_allocated(0) / 1e9 if torch.cuda.is_available() else 0
    logger.info(f"VRAM after LoRA: {vram:.1f} GB")

    # 3. Load and format dataset
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
                formatted.insert(0, {"role": "system", "content": system_prompt})

            if config["supports_thinking"] and args.use_thinking:
                if not formatted[0]["content"].endswith("/think"):
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

    # Ensure pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 4. Create trainer
    effective_batch = args.batch_size * args.grad_accum
    logger.info(f"Effective batch size: {effective_batch}")

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        processing_class=tokenizer,
        args=SFTConfig(
            output_dir=os.path.join(args.output_dir, "checkpoints"),
            num_train_epochs=args.epochs,
            per_device_train_batch_size=args.batch_size,
            gradient_accumulation_steps=args.grad_accum,
            learning_rate=args.lr,
            warmup_steps=args.warmup_steps,
            weight_decay=args.weight_decay,
            lr_scheduler_type="cosine",
            max_grad_norm=args.max_grad_norm,
            logging_steps=10,
            save_strategy="epoch",
            save_total_limit=2,
            seed=args.seed,
            bf16=True,
            optim="adamw_8bit",
            report_to=["none"],
            gradient_checkpointing=True,
            max_seq_length=max_seq_length,
            dataset_num_proc=2,
            remove_unused_columns=False,
        ),
        formatting_func=lambda ex: ex["text"],
    )

    # 5. Train
    logger.info("=" * 60)
    logger.info("Starting training")
    logger.info("=" * 60)

    start_time = time.time()
    try:
        trainer.train()
    except torch.cuda.OutOfMemoryError:
        logger.error("OOM! Reduce batch_size, max_seq_length, or lora_r")
        raise
    except Exception as e:
        logger.error(f"Training failed: {e}")
        traceback.print_exc()
        raise

    elapsed = time.time() - start_time
    logger.info(f"Training completed in {elapsed / 60:.1f} minutes")

    # 6. Save adapters
    adapters_dir = os.path.join(args.output_dir, f"{args.output_name}-lora")
    model.save_pretrained(adapters_dir)
    tokenizer.save_pretrained(adapters_dir)
    logger.info(f"LoRA adapters saved to {adapters_dir}")

    # 7. Optionally save merged model
    if args.save_merged:
        merged_dir = os.path.join(args.output_dir, f"{args.output_name}-merged-16bit")
        model.save_pretrained_merged(merged_dir, tokenizer, save_method="merged_16bit")
        logger.info(f"Merged model saved to {merged_dir}")

    # 8. Optionally export GGUF
    if args.export_gguf:
        gguf_dir = os.path.join(args.output_dir, f"{args.output_name}-gguf")
        model.save_pretrained_gguf(gguf_dir, tokenizer, quantization_method=args.gguf_quant)
        logger.info(f"GGUF exported to {gguf_dir}")

    # 9. Quick eval
    logger.info("Running quick evaluation...")
    FastLanguageModel.for_inference(model)

    test_prompt = "Explain the key differences between CRISPR-Cas9 and base editing in gene therapy."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": test_prompt},
    ]
    inputs = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(inputs, max_new_tokens=256, temperature=0.7, do_sample=True)
    response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
    logger.info(f"Eval response: {response[:300]}...")

    logger.info("=" * 60)
    logger.info("CAJAL training pipeline completed!")
    logger.info("=" * 60)

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return 0


if __name__ == "__main__":
    sys.exit(main())