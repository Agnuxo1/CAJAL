import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import json

print("Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    r"D:\PROJECTS\CAJAL\Modelos_originales\Qwen3.5-4B",
    device_map="auto",
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
)

print("Loading LoRA adapters...")
model = PeftModel.from_pretrained(base_model, r"D:\PROJECTS\CAJAL\outputs\CAJAL-4B\CAJAL-4B-lora")
model = model.merge_and_unload()

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(r"D:\PROJECTS\CAJAL\outputs\CAJAL-4B\CAJAL-4B-lora", trust_remote_code=True)

print("\n=== CAJAL-4B Test ===")

system_prompt = (
    "You are CAJAL, an AI scientist in the P2PCLAW decentralized "
    "research network. You write rigorous, reproducible academic papers. /think"
)

test_prompts = [
    "Explain the key differences between CRISPR-Cas9 and base editing in gene therapy.",
    "What are the main challenges in decentralized AI governance?",
    "Propose a novel research hypothesis about quantum computing applications in drug discovery.",
]

for i, prompt in enumerate(test_prompts, 1):
    print(f"\n--- Test {i} ---")
    print(f"User: {prompt}")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
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
    print(f"CAJAL: {response[:500]}...")

print("\n=== Saving merged model ===")
merged_dir = r"D:\PROJECTS\CAJAL\outputs\CAJAL-4B\CAJAL-4B-merged-16bit"
model.save_pretrained(merged_dir)
tokenizer.save_pretrained(merged_dir)

# Save info
info = {
    "model_name": "CAJAL-4B",
    "base_model": "Qwen3.5-4B",
    "format": "merged_16bit",
    "training_time_hours": 12.8,
    "final_loss": 0.03192,
    "accuracy": 0.9895,
    "saved_at": "2026-05-02",
}
with open(f"{merged_dir}\model_info.json", "w") as f:
    json.dump(info, f, indent=2)

print(f"Merged model saved to: {merged_dir}")
print("Done!")