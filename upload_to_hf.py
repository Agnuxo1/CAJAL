#!/usr/bin/env python3
"""
Upload CAJAL-4B model to HuggingFace Hub
"""
import io
import os
import sys
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Set your HuggingFace token here or via environment variable
os.environ["HF_TOKEN"] = os.environ.get("HF_TOKEN", "your-hf-token-here")

from huggingface_hub import HfApi, create_repo, upload_file, upload_folder

REPO_ID = "Agnuxo/CAJAL-4B-P2PCLAW"
MODEL_DIR = Path(r"D:\PROJECTS\CAJAL\outputs\CAJAL-4B\CAJAL-4B-merged-16bit")
LOGO_BLUE = Path(r"D:\PROJECTS\CAJAL\Neuro-Cajal.png")
LOGO_ORANGE = Path(r"D:\PROJECTS\CAJAL\Neuro-Cajal-2.png")

def main():
    api = HfApi()
    
    print(f"CAJAL-4B HuggingFace Upload")
    print(f"Repository: {REPO_ID}")
    print(f"Model dir: {MODEL_DIR}")
    print("-" * 50)
    
    # 1. Create repo if not exists
    try:
        create_repo(REPO_ID, repo_type="model", private=False, exist_ok=True)
        print("✅ Repository ready")
    except Exception as e:
        print(f"⚠️ Repo creation: {e}")
    
    # 2. Upload model files
    print("\n📤 Uploading model files...")
    files_to_upload = [
        "config.json",
        "generation_config.json",
        "model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
        "chat_template.jinja",
        "model_info.json",
        "README.md",
    ]
    
    for fname in files_to_upload:
        fpath = MODEL_DIR / fname
        if fpath.exists():
            print(f"  Uploading {fname} ({fpath.stat().st_size / 1024 / 1024:.1f} MB)...")
            try:
                upload_file(
                    path_or_fileobj=str(fpath),
                    path_in_repo=fname,
                    repo_id=REPO_ID,
                    repo_type="model",
                )
                print(f"    ✅ {fname}")
            except Exception as e:
                print(f"    ❌ {fname}: {e}")
        else:
            print(f"  ⚠️ Missing: {fname}")
    
    # 3. Upload logos
    print("\n📤 Uploading logos...")
    for logo_path, logo_name in [(LOGO_BLUE, "logo_cajal_blue.png"), (LOGO_ORANGE, "logo_cajal_orange.png")]:
        if logo_path.exists():
            print(f"  Uploading {logo_name}...")
            try:
                upload_file(
                    path_or_fileobj=str(logo_path),
                    path_in_repo=logo_name,
                    repo_id=REPO_ID,
                    repo_type="model",
                )
                print(f"    ✅ {logo_name}")
            except Exception as e:
                print(f"    ❌ {logo_name}: {e}")
        else:
            print(f"  ⚠️ Logo not found: {logo_path}")
    
    print(f"\n{'='*50}")
    print(f"🎉 Upload complete!")
    print(f"🔗 https://huggingface.co/{REPO_ID}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
