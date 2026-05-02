#!/usr/bin/env python3
"""
Create MEGA dataset by combining ALL available training data:
- Enhanced CAJAL-9B agent workflow dataset (135 examples)
- Original CAJAL-9B dataset (42 examples)
- P2PCLAW full training dataset (669 examples)
- P2PCLAW high-quality dataset (487 examples)
- P2PCLAW reasoning dataset (1461 examples)
- P2PCLAW tool-use dataset (960 examples)

Total target: ~3500+ examples
"""

import json
import random
import sys
import io
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def load_jsonl(path):
    """Load a JSONL file."""
    examples = []
    if not Path(path).exists():
        print(f"  [SKIP] Not found: {path}")
        return examples
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    examples.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return examples

def format_to_messages(example):
    """Ensure example has 'messages' format."""
    if "messages" in example:
        return example
    # Try to convert from other formats
    if "conversations" in example:
        return {"messages": example["conversations"]}
    if "instruction" in example and "output" in example:
        return {"messages": [
            {"role": "user", "content": example["instruction"]},
            {"role": "assistant", "content": example["output"]}
        ]}
    if "prompt" in example and "completion" in example:
        return {"messages": [
            {"role": "user", "content": example["prompt"]},
            {"role": "assistant", "content": example["completion"]}
        ]}
    return None

def main():
    print("Building MEGA CAJAL-9B Dataset")
    print("=" * 60)
    
    all_examples = []
    sources = []
    
    # 1. Enhanced agent workflow dataset
    print("\n[1/6] Loading enhanced agent workflow dataset...")
    ex = load_jsonl("datasets/cajal_9b_enhanced_dataset.jsonl")
    all_examples.extend(ex)
    sources.append(("Enhanced Agent Workflow", len(ex)))
    
    # 2. Original agent workflow dataset
    print("[2/6] Loading original agent workflow dataset...")
    ex = load_jsonl("datasets/cajal_9b_agent_dataset.jsonl")
    all_examples.extend(ex)
    sources.append(("Original Agent Workflow", len(ex)))
    
    # 3. P2PCLAW full training
    print("[3/6] Loading P2PCLAW full training dataset...")
    ex = load_jsonl("datasets/p2pclaw_train_full_qwen3.jsonl")
    all_examples.extend(ex)
    sources.append(("P2PCLAW Full", len(ex)))
    
    # 4. P2PCLAW high-quality
    print("[4/6] Loading P2PCLAW high-quality dataset...")
    ex = load_jsonl("datasets/p2pclaw_train_hq_qwen3.jsonl")
    all_examples.extend(ex)
    sources.append(("P2PCLAW High-Quality", len(ex)))
    
    # 5. P2PCLAW reasoning
    print("[5/6] Loading P2PCLAW reasoning dataset...")
    ex = load_jsonl("datasets/p2pclaw_train_reasoning_qwen3.jsonl")
    all_examples.extend(ex)
    sources.append(("P2PCLAW Reasoning", len(ex)))
    
    # 6. P2PCLAW tool-use
    print("[6/6] Loading P2PCLAW tool-use dataset...")
    ex = load_jsonl("datasets/p2pclaw_train_tooluse_qwen3.jsonl")
    all_examples.extend(ex)
    sources.append(("P2PCLAW Tool-Use", len(ex)))
    
    print("\n" + "=" * 60)
    print("Source Statistics:")
    for name, count in sources:
        print(f"  {name}: {count}")
    print(f"\n  RAW TOTAL: {len(all_examples)}")
    
    # Convert all to standard format
    print("\nConverting to standard message format...")
    formatted = []
    skipped = 0
    for ex in all_examples:
        conv = format_to_messages(ex)
        if conv and "messages" in conv and len(conv["messages"]) >= 2:
            formatted.append(conv)
        else:
            skipped += 1
    
    print(f"  Formatted: {len(formatted)}")
    print(f"  Skipped: {skipped}")
    
    # Shuffle
    random.shuffle(formatted)
    
    # Save
    output_path = "datasets/cajal_9b_mega_dataset.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in formatted:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    
    # Calculate size
    file_size_mb = Path(output_path).stat().st_size / (1024 * 1024)
    
    print("\n" + "=" * 60)
    print(f"MEGA DATASET SAVED: {output_path}")
    print(f"Total examples: {len(formatted)}")
    print(f"File size: {file_size_mb:.1f} MB")
    print("=" * 60)
    print("\nThis dataset combines:")
    print("  - Agent workflow procedures (Step 1-14)")
    print("  - P2PCLAW platform knowledge")
    print("  - Real paper analysis from Railway")
    print("  - Python code and Lean 4 verification")
    print("  - Original P2PCLAW training data (reasoning, tool-use, etc.)")
    print("=" * 60)

if __name__ == "__main__":
    main()
