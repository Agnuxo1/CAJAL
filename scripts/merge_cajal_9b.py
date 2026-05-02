#!/usr/bin/env python3
"""
Merge CAJAL-9B LoRA adapters with base model and save as 16-bit merged model.
Also runs a quick inference test.

Usage:
    python scripts/merge_cajal_9b.py
"""

import sys
import io
import json
import os

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = r"D:\PROJECTS\CAJAL\Modelos_originales\Qwen3.5-9B"
ADAPTER_DIR = r"D:\PROJECTS\CAJAL\outputs\CAJAL-9B\CAJAL-9B-lora"
MERGED_DIR = r"D:\PROJECTS\CAJAL\outputs\CAJAL-9B\CAJAL-9B-merged-16bit"

def main():
    print("=" * 60)
    print("CAJAL-9B: Merge LoRA Adapters")
    print("=" * 60)
    
    print("\n[1/5] Loading base model (Qwen3.5-9B)...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    print(f"   Base model loaded: {type(model).__name__}")
    
    print("\n[2/5] Loading LoRA adapters...")
    model = PeftModel.from_pretrained(model, ADAPTER_DIR)
    print("   Adapters loaded")
    
    print("\n[3/5] Merging adapters into base model...")
    model = model.merge_and_unload()
    print("   Merge complete")
    
    print(f"\n[4/5] Saving merged model to: {MERGED_DIR}")
    os.makedirs(MERGED_DIR, exist_ok=True)
    model.save_pretrained(MERGED_DIR, safe_serialization=True, max_shard_size="5GB")
    print("   Model saved")
    
    print("\n[5/5] Saving tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(ADAPTER_DIR, trust_remote_code=True)
    tokenizer.save_pretrained(MERGED_DIR)
    print("   Tokenizer saved")
    
    # Copy training info
    info_src = os.path.join(ADAPTER_DIR, "training_info.json")
    info_dst = os.path.join(MERGED_DIR, "training_info.json")
    if os.path.exists(info_src):
        import shutil
        shutil.copy(info_src, info_dst)
        print("   Training info copied")
    
    # Test inference
    print("\n" + "=" * 60)
    print("Running inference test...")
    print("=" * 60)
    
    system_prompt_path = r"D:\PROJECTS\CAJAL\cajal_9b_system_prompt.txt"
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read().strip()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "I want to write a paper about Byzantine Fault Tolerance in Gossip Protocols. What is the first step?"},
    ]
    
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    print("\nGenerating response (this may take a minute)...")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    print("\n--- MODEL RESPONSE ---")
    print(response[:1000])
    print("..." if len(response) > 1000 else "")
    print("--- END RESPONSE ---")
    
    print("\n" + "=" * 60)
    print("CAJAL-9B merged model saved successfully!")
    print(f"Location: {MERGED_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
