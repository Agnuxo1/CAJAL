import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import gc

model_path = r"D:\PROJECTS\CAJAL\Modelos_originales\Qwen3.5-9B"

print("Testing Qwen3.5-9B load with AutoModelForCausalLM...")
try:
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    print(f"[OK] Tokenizer loaded. Vocab size: {len(tokenizer)}")
    
    from transformers import BitsAndBytesConfig
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    print(f"[OK] Model loaded successfully!")
    print(f"   Model class: {type(model).__name__}")
    
    text = "Explain peer-to-peer network consensus:"
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    print(f"[OK] Tokenizer test passed. Input shape: {inputs.input_ids.shape}")
    
    del model
    gc.collect()
    torch.cuda.empty_cache()
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
