#!/usr/bin/env python3
"""
CAJAL Fine-Tuning Script
Optimized for NVIDIA RTX 3090 (24GB VRAM) using Unsloth + QLoRA
Supports: Qwen3-4B, Qwen3-8B, Gemma 4 E4B, Gemma 4 26B MoE

Usage:
    python train_cajal.py \
        --model qwen3-4b \
        --dataset ./datasets/papers.jsonl \
        --output-name CAJAL \
        --epochs 3 \
        --export-gguf
"""

import argparse
import gc
import json
import logging
import os
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn
from datasets import Dataset, load_dataset
from transformers import (
    TrainingArguments,
    AutoTokenizer,
)
from trl import SFTTrainer, SFTConfig

# Unsloth imports (optional - falls back to transformers on Windows)
try:
    from unsloth import FastLanguageModel, is_bfloat16_supported
    from unsloth.chat_templates import get_chat_template, train_on_responses_only
    UNSLOTH_AVAILABLE = True
except ImportError:
    UNSLOTH_AVAILABLE = False
    FastLanguageModel = None
    def is_bfloat16_supported():
        return torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 8
    get_chat_template = None
    train_on_responses_only = None

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("cajal_training.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("CAJAL")

# ---------------------------------------------------------------------------
# Model variant naming
# ---------------------------------------------------------------------------
MODEL_VARIANTS = {
    "qwen3-4b": "CAJAL-4B",
    "qwen3-8b": "CAJAL-8B",
    "qwen3.5-27b": "CAJAL-27B",
    "gemma4-e4b": "CAJAL-G4E",
    "gemma4-26b": "CAJAL-G26B",
}

# ---------------------------------------------------------------------------
# Model configurations
# ---------------------------------------------------------------------------
MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "qwen3-4b": {
        "model_id": "unsloth/Qwen3-4B-unsloth-bnb-4bit",
        "chat_template": "qwen3",
        "max_seq_length_default": 32768,
        "lora_target_modules": [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        "supports_thinking": True,
        "system_prompt": (
            "You are CAJAL, an expert AI research assistant "
            "specialized in scientific literature analysis, hypothesis generation, "
            "and experimental design. Always reason step-by-step and cite sources "
            "when possible."
        ),
    },
    "qwen3-8b": {
        "model_id": "unsloth/Qwen3-8B-unsloth-bnb-4bit",
        "chat_template": "qwen3",
        "max_seq_length_default": 32768,
        "lora_target_modules": [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        "supports_thinking": True,
        "system_prompt": (
            "You are CAJAL, an expert AI research assistant "
            "specialized in scientific literature analysis, hypothesis generation, "
            "and experimental design. Always reason step-by-step and cite sources "
            "when possible."
        ),
    },
    "gemma4-e4b": {
        "model_id": "unsloth/gemma-4-e4b-it-unsloth-bnb-4bit",
        "chat_template": "gemma-4",
        "max_seq_length_default": 8192,
        "lora_target_modules": [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        "supports_thinking": False,
        "system_prompt": (
            "You are CAJAL, an expert AI research assistant "
            "specialized in scientific literature analysis, hypothesis generation, "
            "and experimental design."
        ),
    },
    "gemma4-26b": {
        "model_id": "unsloth/gemma-4-26b-it-unsloth-bnb-4bit",
        "chat_template": "gemma-4",
        "max_seq_length_default": 8192,
        "lora_target_modules": [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        "supports_thinking": False,
        "system_prompt": (
            "You are CAJAL, an expert AI research assistant "
            "specialized in scientific literature analysis, hypothesis generation, "
            "and experimental design."
        ),
    },
    "qwen3.5-27b": {
        "model_id": "local",  # overridden by --local-model-path
        "chat_template": "qwen3",
        "max_seq_length_default": 4096,
        "lora_target_modules": [
            # Standard full_attention and MLP modules
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
            # Linear attention / Mamba2 / SSM modules
            "A_log", "dt_bias", "conv1d",
            "in_proj_a", "in_proj_b", "in_proj_qkv", "in_proj_z",
            "out_proj", "norm",
        ],
        "supports_thinking": True,
        "system_prompt": (
            "You are CAJAL, an AI scientist in the P2PCLAW decentralized "
            "research network. You write rigorous, reproducible academic papers "
            "with structured methodology, statistical analysis, Lean 4 proofs, "
            "and proper citations. Always reason step-by-step and ground "
            "claims in evidence."
        ),
    },
}

# ---------------------------------------------------------------------------
# VRAM utilities
# ---------------------------------------------------------------------------
def get_gpu_memory_info() -> Dict[str, float]:
    """Return GPU memory stats in MB."""
    if not torch.cuda.is_available():
        return {}
    props = torch.cuda.get_device_properties(0)
    total = props.total_memory / (1024 ** 2)
    allocated = torch.cuda.memory_allocated(0) / (1024 ** 2)
    reserved = torch.cuda.memory_reserved(0) / (1024 ** 2)
    free = total - allocated
    return {
        "total_mb": round(total, 2),
        "allocated_mb": round(allocated, 2),
        "reserved_mb": round(reserved, 2),
        "free_mb": round(free, 2),
    }


def print_vram_banner(stage: str) -> None:
    """Print a VRAM usage banner."""
    mem = get_gpu_memory_info()
    if not mem:
        logger.info("[VRAM] No CUDA device available")
        return
    logger.info(
        f"[VRAM: {stage}] Total: {mem['total_mb']:.0f}MB | "
        f"Allocated: {mem['allocated_mb']:.0f}MB | "
        f"Reserved: {mem['reserved_mb']:.0f}MB | "
        f"Free: {mem['free_mb']:.0f}MB"
    )


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fine-tune CAJAL on scientific papers using Unsloth+QLoRA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--model",
        default="qwen3-4b",
        choices=["qwen3-4b", "qwen3-8b", "qwen3.5-27b", "gemma4-e4b", "gemma4-26b"],
        help="Base model to fine-tune",
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Path to JSONL dataset file with chat-formatted conversations",
    )
    parser.add_argument(
        "--local-model-path",
        default=None,
        help="Local path to model directory (required for qwen3.5-27b and custom models)",
    )
    parser.add_argument(
        "--output-dir",
        default="./outputs",
        help="Directory for all outputs",
    )
    parser.add_argument(
        "--output-name",
        default="CAJAL",
        help="Name prefix for saved models and adapters",
    )
    parser.add_argument(
        "--lora-r", type=int, default=32,
        help="LoRA rank (higher = more capacity, more VRAM)",
    )
    parser.add_argument(
        "--lora-alpha", type=int, default=64,
        help="LoRA alpha (typically 2x r)",
    )
    parser.add_argument(
        "--lora-dropout", type=float, default=0.0,
        help="LoRA dropout (0 recommended for QLoRA)",
    )
    parser.add_argument(
        "--epochs", type=int, default=3,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--batch-size", type=int, default=2,
        help="Per-device batch size",
    )
    parser.add_argument(
        "--grad-accum", type=int, default=4,
        help="Gradient accumulation steps (effective batch = batch * grad_accum)",
    )
    parser.add_argument(
        "--lr", type=float, default=2e-4,
        help="Learning rate",
    )
    parser.add_argument(
        "--max-seq-length", type=int, default=8192,
        help="Maximum sequence length for training",
    )
    parser.add_argument(
        "--warmup-ratio", type=float, default=0.1,
        help="Warmup ratio of total steps",
    )
    parser.add_argument(
        "--weight-decay", type=float, default=0.01,
        help="Weight decay",
    )
    parser.add_argument(
        "--max-grad-norm", type=float, default=0.3,
        help="Max gradient norm for clipping",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed",
    )
    parser.add_argument(
        "--export-gguf", action="store_true",
        help="Export trained model to GGUF format for Ollama",
    )
    parser.add_argument(
        "--gguf-quant", default="q4_k_m",
        choices=["q4_0", "q4_k_m", "q5_k_m", "q8_0", "f16"],
        help="GGUF quantization type",
    )
    parser.add_argument(
        "--save-merged", action="store_true",
        help="Also save a full 16-bit merged model",
    )
    parser.add_argument(
        "--resume-from-checkpoint",
        default=None,
        help="Resume training from a checkpoint directory",
    )
    parser.add_argument(
        "--use-thinking", action="store_true",
        help="Enable thinking mode for Qwen3 models",
    )
    parser.add_argument(
        "--eval-sample",
        default=None,
        help="Path to evaluation JSONL for post-training benchmark",
    )
    parser.add_argument(
        "--skip-eval", action="store_true",
        help="Skip post-training evaluation",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Console logging level",
    )
    parser.add_argument(
        "--use-rslora", action="store_true",
        help="Use Rank-Stabilized LoRA (better for high ranks)",
    )
    parser.add_argument(
        "--num-procs", type=int, default=4,
        help="Number of processes for dataset mapping",
    )
    parser.add_argument(
        "--load-in-4bit", action="store_true", default=True,
        help="Load model in 4-bit (QLoRA). Default True.",
    )
    parser.add_argument(
        "--load-in-8bit", action="store_true",
        help="Load model in 8-bit instead of 4-bit (more VRAM, better quality)",
    )

    args = parser.parse_args()

    if args.load_in_8bit:
        args.load_in_4bit = False

    return args


# ---------------------------------------------------------------------------
# Dataset loading & formatting
# ---------------------------------------------------------------------------
def load_jsonl_dataset(path: str) -> Dataset:
    """Load a JSONL dataset where each line is a conversation list."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    logger.info(f"Loading dataset from {path}")
    data: List[Dict[str, Any]] = []
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

            # Normalize to a list of messages
            if isinstance(obj, list) and all(isinstance(m, dict) for m in obj):
                messages = obj
            elif isinstance(obj, dict) and "messages" in obj:
                messages = obj["messages"]
            elif isinstance(obj, dict) and "conversations" in obj:
                messages = obj["conversations"]
            elif isinstance(obj, dict) and "instruction" in obj:
                # Alpaca-style -> chat format
                messages = [
                    {"role": "user", "content": obj["instruction"]},
                    {"role": "assistant", "content": obj.get("output", obj.get("response", ""))},
                ]
            else:
                logger.warning(f"Skipping unrecognized format on line {line_num}")
                continue

            data.append({"messages": messages})

    logger.info(f"Loaded {len(data)} conversations")
    return Dataset.from_list(data)


def format_dataset_with_chat_template(
    dataset: Dataset,
    tokenizer: Any,
    model_choice: str,
    system_prompt: str,
    supports_thinking: bool,
    use_thinking: bool,
    num_proc: int = 4,
) -> Dataset:
    """Apply the model's chat template to the dataset."""

    logger.info(f"Applying chat template for {model_choice}")

    def apply_template(examples: Dict[str, Any]) -> Dict[str, Any]:
        texts = []
        for messages in examples["messages"]:
            # Ensure messages is a list of dicts with role/content
            formatted = []
            for msg in messages:
                role = msg.get("role", msg.get("from", "user"))
                content = msg.get("content", msg.get("value", msg.get("text", "")))
                if role in ("human", "user"):
                    role = "user"
                elif role in ("gpt", "assistant", "model"):
                    role = "assistant"
                formatted.append({"role": role, "content": content})

            # Inject system prompt at beginning if not present
            if formatted and formatted[0].get("role") != "system":
                formatted.insert(0, {"role": "system", "content": system_prompt})

            # For Qwen3 thinking mode: append /think or /no_think to system prompt
            if supports_thinking and use_thinking:
                if formatted[0]["content"].endswith("/no_think"):
                    formatted[0]["content"] = formatted[0]["content"].replace("/no_think", "/think")
                elif not formatted[0]["content"].endswith("/think"):
                    formatted[0]["content"] += " /think"

            try:
                text = tokenizer.apply_chat_template(
                    formatted,
                    tokenize=False,
                    add_generation_prompt=False,
                )
            except Exception as e:
                logger.warning(f"Chat template error: {e}. Falling back to simple concat.")
                text = "\n\n".join(f"{m['role']}: {m['content']}" for m in formatted)

            texts.append(text)
        return {"text": texts}

    dataset = dataset.map(
        apply_template,
        batched=True,
        num_proc=num_proc,
        desc="Applying chat template",
    )
    return dataset


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
def load_model_and_tokenizer(
    model_choice: str,
    max_seq_length: int,
    load_in_4bit: bool = True,
    load_in_8bit: bool = False,
    local_model_path: Optional[str] = None,
) -> tuple:
    """Load base model and tokenizer via Unsloth."""
    config = MODEL_CONFIGS[model_choice]
    model_id = local_model_path if local_model_path else config["model_id"]
    chat_template_name = config["chat_template"]

    logger.info(f"Loading model: {model_id}")
    logger.info(f"Max sequence length: {max_seq_length}")
    logger.info(f"Quantization: {'8-bit' if load_in_8bit else '4-bit (QLoRA)'}")
    logger.info(f"Unsloth available: {UNSLOTH_AVAILABLE}")

    if UNSLOTH_AVAILABLE:
        dtype = torch.bfloat16 if is_bfloat16_supported() else torch.float16
        logger.info(f"Using dtype: {dtype}")
        try:
            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=model_id,
                max_seq_length=max_seq_length,
                dtype=dtype,
                load_in_4bit=load_in_4bit and not load_in_8bit,
                load_in_8bit=load_in_8bit,
                full_finetuning=False,
            )
            logger.info("Model loaded via Unsloth FastLanguageModel")
        except Exception as e:
            logger.warning(f"Unsloth FastLanguageModel failed: {e}")
            logger.info("Falling back to standard transformers + bitsandbytes...")
            model, tokenizer = _load_with_transformers(
                model_id, max_seq_length, load_in_4bit, load_in_8bit
            )
    else:
        logger.info("Unsloth not available, using transformers + bitsandbytes directly")
        model, tokenizer = _load_with_transformers(
            model_id, max_seq_length, load_in_4bit, load_in_8bit
        )

    # Apply chat template to tokenizer
    if get_chat_template:
        tokenizer = get_chat_template(
            tokenizer,
            chat_template=chat_template_name,
        )
    else:
        from transformers import AutoTokenizer
        # Use the tokenizer's own chat_template attribute
        logger.info("Using tokenizer's built-in chat template")

    # Ensure pad token is set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print_vram_banner("After Model Load")
    return model, tokenizer


def _load_with_transformers(
    model_id: str,
    max_seq_length: int,
    load_in_4bit: bool,
    load_in_8bit: bool,
) -> tuple:
    """Fallback: load model via standard transformers + bitsandbytes."""
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    bnb_config = None
    if load_in_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16 if is_bfloat16_supported() else torch.float16,
            bnb_4bit_use_double_quant=True,
        )
    elif load_in_8bit:
        bnb_config = BitsAndBytesConfig(load_in_8bit=True)

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16 if is_bfloat16_supported() else torch.float16,
    )

    logger.info("Model loaded via standard transformers fallback")
    return model, tokenizer


# ---------------------------------------------------------------------------
# LoRA configuration
# ---------------------------------------------------------------------------
def setup_lora(
    model: nn.Module,
    model_choice: str,
    lora_r: int,
    lora_alpha: int,
    lora_dropout: float,
    use_rslora: bool,
) -> nn.Module:
    """Attach LoRA adapters to the model."""
    config = MODEL_CONFIGS[model_choice]
    target_modules = config["lora_target_modules"]

    logger.info(
        f"Configuring LoRA: r={lora_r}, alpha={lora_alpha}, "
        f"dropout={lora_dropout}, rslora={use_rslora}"
    )
    logger.info(f"Target modules: {target_modules}")

    if UNSLOTH_AVAILABLE:
        model = FastLanguageModel.get_peft_model(
            model,
            r=lora_r,
            target_modules=target_modules,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=42,
            use_rslora=use_rslora,
        )
    else:
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        model = prepare_model_for_kbit_training(model)
        lora_config = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=target_modules,
            use_rslora=use_rslora,
        )
        model = get_peft_model(model, lora_config)

    logger.info("LoRA adapters attached successfully")
    print_vram_banner("After LoRA Setup")
    return model


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
def create_trainer(
    model: nn.Module,
    tokenizer: Any,
    train_dataset: Dataset,
    model_choice: str,
    args: argparse.Namespace,
) -> SFTTrainer:
    """Create and configure the SFTTrainer."""

    effective_batch = args.batch_size * args.grad_accum
    logger.info(f"Effective batch size: {effective_batch}")

    # Training arguments optimized for RTX 3090
    training_args = SFTConfig(
        output_dir=os.path.join(args.output_dir, "checkpoints"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        warmup_steps=100,
        weight_decay=args.weight_decay,
        lr_scheduler_type="cosine",
        max_grad_norm=args.max_grad_norm,
        logging_steps=10,
        save_strategy="epoch",
        save_total_limit=2,
        seed=args.seed,
        bf16=is_bfloat16_supported(),
        fp16=not is_bfloat16_supported(),
        optim="adamw_8bit",
        report_to=["none"],
        gradient_checkpointing=True,
        dataloader_num_workers=0,  # 0 for Windows stability
        remove_unused_columns=False,
    )

    # Unsloth supports packing, which speeds up training significantly
    max_seq_length = args.max_seq_length

    # Set tokenizer max length for truncation during tokenization
    tokenizer.model_max_length = max_seq_length

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        processing_class=tokenizer,
        formatting_func=lambda ex: ex["text"],
    )

    logger.info("Trainer configured")
    return trainer


def run_training(
    trainer: SFTTrainer,
    resume_from_checkpoint: Optional[str] = None,
) -> Any:
    """Run the training loop with error handling."""
    logger.info("=" * 60)
    logger.info("Starting training")
    logger.info("=" * 60)
    print_vram_banner("Before Training")

    start_time = time.time()
    try:
        if resume_from_checkpoint and os.path.isdir(resume_from_checkpoint):
            logger.info(f"Resuming from checkpoint: {resume_from_checkpoint}")
            train_result = trainer.train(resume_from_checkpoint=resume_from_checkpoint)
        else:
            train_result = trainer.train()
    except torch.cuda.OutOfMemoryError as e:
        logger.error(f"OOM during training: {e}")
        logger.error("Suggestions: reduce batch_size, max_seq_length, or lora_r")
        raise
    except Exception as e:
        logger.error(f"Training failed: {e}")
        traceback.print_exc()
        raise

    elapsed = time.time() - start_time
    logger.info(f"Training completed in {elapsed / 60:.2f} minutes")
    print_vram_banner("After Training")

    return train_result


# ---------------------------------------------------------------------------
# Saving / Exporting
# ---------------------------------------------------------------------------
def save_lora_adapters(
    model: nn.Module,
    tokenizer: Any,
    output_dir: str,
    output_name: str,
) -> str:
    """Save LoRA adapters."""
    adapters_dir = os.path.join(output_dir, f"{output_name}-lora")
    os.makedirs(adapters_dir, exist_ok=True)

    logger.info(f"Saving LoRA adapters to {adapters_dir}")
    model.save_pretrained(adapters_dir)
    tokenizer.save_pretrained(adapters_dir)

    # Save training info
    info = {
        "model_name": output_name,
        "adapter_format": "PEFT LoRA",
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(os.path.join(adapters_dir, "adapter_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

    logger.info("LoRA adapters saved")
    return adapters_dir


def save_merged_model(
    model: nn.Module,
    tokenizer: Any,
    output_dir: str,
    output_name: str,
) -> str:
    """Merge LoRA adapters into base model and save as 16-bit."""
    merged_dir = os.path.join(output_dir, f"{output_name}-merged-16bit")
    os.makedirs(merged_dir, exist_ok=True)

    logger.info(f"Saving merged 16-bit model to {merged_dir}")

    if UNSLOTH_AVAILABLE:
        model.save_pretrained_merged(
            merged_dir,
            tokenizer,
            save_method="merged_16bit",
        )
    else:
        from peft import PeftModel
        merged_model = model.merge_and_unload()
        merged_model.save_pretrained(merged_dir)
        tokenizer.save_pretrained(merged_dir)

    logger.info("Merged 16-bit model saved")
    return merged_dir


def export_gguf(
    model: nn.Module,
    tokenizer: Any,
    output_dir: str,
    output_name: str,
    quantization: str,
) -> str:
    """Export to GGUF format for Ollama / LM Studio."""
    gguf_dir = os.path.join(output_dir, f"{output_name}-gguf")
    os.makedirs(gguf_dir, exist_ok=True)

    logger.info(f"Exporting GGUF with quantization={quantization} to {gguf_dir}")

    if UNSLOTH_AVAILABLE:
        model.save_pretrained_gguf(
            gguf_dir,
            tokenizer,
            quantization_method=quantization,
        )
    else:
        logger.warning("GGUF export requires Unsloth. Saving merged HF model instead.")
        from peft import PeftModel
        merged = model.merge_and_unload()
        merged.save_pretrained(gguf_dir)
        tokenizer.save_pretrained(gguf_dir)

    logger.info("GGUF export complete")
    return gguf_dir


def create_ollama_modelfile(
    gguf_path: str,
    output_dir: str,
    output_name: str,
    system_prompt: str,
) -> str:
    """Create an Ollama Modelfile for easy import."""
    modelfile_path = os.path.join(output_dir, "Ollama-Modelfile")

    # Find the .gguf file inside gguf_path
    gguf_files = [f for f in os.listdir(gguf_path) if f.endswith(".gguf")]
    if not gguf_files:
        logger.warning("No .gguf file found; skipping Modelfile creation")
        return ""

    gguf_file = gguf_files[0]
    # Relative path from where Modelfile will be used
    content = f"""FROM ./{os.path.basename(gguf_path)}/{gguf_file}

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1

SYSTEM '''{system_prompt}'''
"""

    with open(modelfile_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Ollama Modelfile created at {modelfile_path}")
    return modelfile_path


# ---------------------------------------------------------------------------
# Post-training evaluation
# ---------------------------------------------------------------------------
def generate_sample(
    model: nn.Module,
    tokenizer: Any,
    prompt: str,
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """Generate text from a prompt."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to(model.device)

    with torch.no_grad():
        start = time.time()
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
        elapsed = time.time() - start

    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Remove prompt from output for cleaner display
    if prompt in generated:
        generated = generated[len(prompt):].strip()

    tokens_generated = outputs.shape[1] - inputs["input_ids"].shape[1]
    tps = tokens_generated / elapsed if elapsed > 0 else 0
    return generated, tps


def run_evaluation(
    model: nn.Module,
    tokenizer: Any,
    model_choice: str,
    system_prompt: str,
    eval_path: Optional[str],
    output_dir: str,
    output_name: str,
) -> None:
    """Run post-training evaluation."""
    logger.info("=" * 60)
    logger.info("Post-Training Evaluation")
    logger.info("=" * 60)

    # Enable inference mode
    if UNSLOTH_AVAILABLE:
        FastLanguageModel.for_inference(model)
    else:
        model.eval()

    # Test prompts for scientific research assistant
    test_prompts = [
        {
            "name": "Hypothesis Generation",
            "prompt": "Generate a novel research hypothesis about the intersection of machine learning and CRISPR gene editing, including a proposed experimental design.",
        },
        {
            "name": "Paper Summary",
            "prompt": "Summarize the key contributions, methodology, and limitations of a hypothetical paper on quantum error correction using topological codes.",
        },
        {
            "name": "Literature Gap Analysis",
            "prompt": "What are the current gaps in the literature regarding large language models for scientific discovery? Identify 3 specific underexplored areas.",
        },
    ]

    results = []
    for test in test_prompts:
        logger.info(f"\n--- Test: {test['name']} ---")

        # Build chat-formatted prompt
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": test["prompt"]},
        ]
        try:
            prompt_text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            prompt_text = f"System: {system_prompt}\nUser: {test['prompt']}\nAssistant:"

        generated, tps = generate_sample(model, tokenizer, prompt_text, max_new_tokens=512)
        logger.info(f"Generated ({tps:.1f} tok/s): {generated[:300]}...")

        results.append({
            "test": test["name"],
            "prompt": test["prompt"],
            "response": generated,
            "tokens_per_second": round(tps, 2),
        })

    # If eval dataset provided, run on first N examples
    if eval_path and os.path.isfile(eval_path):
        logger.info(f"\n--- Running on eval dataset: {eval_path} ---")
        try:
            eval_ds = load_jsonl_dataset(eval_path)
            eval_subset = eval_ds.select(range(min(3, len(eval_ds))))
            for i, example in enumerate(eval_subset):
                msgs = example["messages"]
                # Find first user message
                user_msg = next((m for m in msgs if m.get("role") in ("user", "human")), None)
                if not user_msg:
                    continue
                ref_msg = next((m for m in msgs if m.get("role") in ("assistant", "gpt", "model")), None)
                ref_response = ref_msg["content"] if ref_msg else "N/A"

                eval_prompt = tokenizer.apply_chat_template(
                    [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg["content"]},
                    ],
                    tokenize=False,
                    add_generation_prompt=True,
                )
                pred, tps = generate_sample(model, tokenizer, eval_prompt, max_new_tokens=512)
                logger.info(f"Eval {i+1}: User='{user_msg['content'][:60]}...' | "
                            f"Pred='{pred[:150]}...' | Ref='{ref_response[:150]}...'")

                results.append({
                    "test": f"eval_{i+1}",
                    "prompt": user_msg["content"],
                    "response": pred,
                    "reference": ref_response,
                    "tokens_per_second": round(tps, 2),
                })
        except Exception as e:
            logger.warning(f"Eval dataset processing failed: {e}")

    # Save evaluation results
    eval_file = os.path.join(output_dir, f"{output_name}-eval-results.json")
    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Evaluation results saved to {eval_file}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    args = parse_args()
    logger.setLevel(getattr(logging, args.log_level))

    logger.info("=" * 60)
    logger.info("CAJAL Fine-Tuning")
    logger.info("=" * 60)
    logger.info(f"Model choice: {args.model}")
    logger.info(f"Dataset: {args.dataset}")
    logger.info(f"Output name: {args.output_name}")
    logger.info(f"LoRA r={args.lora_r}, alpha={args.lora_alpha}")
    logger.info(f"Epochs={args.epochs}, batch={args.batch_size}, grad_accum={args.grad_accum}")
    logger.info(f"Learning rate={args.lr}, max_seq_length={args.max_seq_length}")
    logger.info(f"Export GGUF={args.export_gguf}, quant={args.gguf_quant}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    print_vram_banner("Startup")

    # Prepare output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Load config
    model_config = MODEL_CONFIGS[args.model]
    system_prompt = model_config["system_prompt"]
    supports_thinking = model_config["supports_thinking"]

    # Override max_seq_length if user specified 0 or too high
    max_seq_length = args.max_seq_length
    if max_seq_length > model_config["max_seq_length_default"]:
        logger.warning(
            f"Requested max_seq_length {max_seq_length} exceeds model default "
            f"{model_config['max_seq_length_default']}. Clamping."
        )
        max_seq_length = model_config["max_seq_length_default"]

    try:
        # 1. Load model & tokenizer
        model, tokenizer = load_model_and_tokenizer(
            args.model,
            max_seq_length=max_seq_length,
            load_in_4bit=args.load_in_4bit,
            load_in_8bit=args.load_in_8bit,
            local_model_path=args.local_model_path,
        )

        # 2. Setup LoRA
        model = setup_lora(
            model,
            args.model,
            args.lora_r,
            args.lora_alpha,
            args.lora_dropout,
            args.use_rslora,
        )

        # 3. Load dataset
        train_dataset = load_jsonl_dataset(args.dataset)
        if len(train_dataset) == 0:
            logger.error("Dataset is empty after loading. Exiting.")
            return 1

        # 4. Format dataset
        train_dataset = format_dataset_with_chat_template(
            train_dataset,
            tokenizer,
            args.model,
            system_prompt,
            supports_thinking,
            args.use_thinking,
            num_proc=args.num_procs,
        )

        # 5. Create trainer
        trainer = create_trainer(
            model,
            tokenizer,
            train_dataset,
            args.model,
            args,
        )

        # 6. Train
        run_training(trainer, resume_from_checkpoint=args.resume_from_checkpoint)

        # 7. Save LoRA adapters
        adapters_dir = save_lora_adapters(
            model,
            tokenizer,
            args.output_dir,
            args.output_name,
        )

        # 8. Optionally save merged model
        if args.save_merged:
            save_merged_model(model, tokenizer, args.output_dir, args.output_name)

        # 9. Optionally export GGUF
        gguf_dir = None
        if args.export_gguf:
            gguf_dir = export_gguf(
                model,
                tokenizer,
                args.output_dir,
                args.output_name,
                args.gguf_quant,
            )
            if gguf_dir:
                create_ollama_modelfile(
                    gguf_dir,
                    args.output_dir,
                    args.output_name,
                    system_prompt,
                )

        # 10. Post-training evaluation
        if not args.skip_eval:
            try:
                run_evaluation(
                    model,
                    tokenizer,
                    args.model,
                    system_prompt,
                    args.eval_sample,
                    args.output_dir,
                    args.output_name,
                )
            except Exception as e:
                logger.warning(f"Evaluation failed (non-critical): {e}")
                traceback.print_exc()

        logger.info("=" * 60)
        logger.info("Fine-tuning pipeline completed successfully!")
        logger.info("=" * 60)
        logger.info(f"LoRA adapters: {adapters_dir}")
        if gguf_dir:
            logger.info(f"GGUF model:    {gguf_dir}")
        logger.info(f"Logs:          {os.path.abspath('cajal_training.log')}")

        return 0

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        traceback.print_exc()
        print_vram_banner("On Error")
        return 1

    finally:
        # Cleanup
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print_vram_banner("Cleanup")


if __name__ == "__main__":
    sys.exit(main())
