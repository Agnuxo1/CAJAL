import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

print("Testing Qwen3.5-4B model load...", flush=True)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

print("Loading tokenizer...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(
    r"D:\PROJECTS\CAJAL\Modelos_originales\Qwen3.5-4B",
    trust_remote_code=True
)
print(f"Tokenizer loaded. Vocab size: {tokenizer.vocab_size}", flush=True)

print("Loading model (4-bit)...", flush=True)
model = AutoModelForCausalLM.from_pretrained(
    r"D:\PROJECTS\CAJAL\Modelos_originales\Qwen3.5-4B",
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
    attn_implementation="eager",
)
print(f"Model loaded: {type(model).__name__}", flush=True)

if torch.cuda.is_available():
    vram = torch.cuda.memory_allocated(0) / 1e9
    print(f"VRAM used: {vram:.2f} GB", flush=True)

print("SUCCESS: Model loads correctly!", flush=True)