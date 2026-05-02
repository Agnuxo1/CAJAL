import sys
import os

output_file = r"D:\PROJECTS\CAJAL\test_result.txt"

try:
    from unsloth import FastLanguageModel
    import torch
    results = []
    results.append(f"PyTorch: {torch.__version__}")
    results.append(f"CUDA: {torch.cuda.is_available()}")
    results.append(f"GPU: {torch.cuda.get_device_name(0)}")
    results.append(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    results.append("Unsloth: imported OK")
    import triton
    results.append(f"Triton: {triton.__version__}")
    results.append("ALL_TESTS_PASSED")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results))
except Exception as e:
    results = [f"ERROR: {type(e).__name__}: {e}"]
    import traceback
    results.append(traceback.format_exc())
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results))