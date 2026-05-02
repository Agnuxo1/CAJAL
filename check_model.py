from transformers import AutoConfig
c = AutoConfig.from_pretrained(r'D:\PROJECTS\CAJAL\Modelos_originales\Qwen3.5-4B', trust_remote_code=True)
print(f'model_type: {c.model_type}')
print(f'architectures: {c.architectures}')
print(f'num_hidden_layers: {getattr(c, "num_hidden_layers", "N/A")}')
print(f'hidden_size: {getattr(c, "hidden_size", "N/A")}')
print(f'vocab_size: {getattr(c, "vocab_size", "N/A")}')