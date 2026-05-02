import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional, Union, List, Dict
import os

DEFAULT_MODEL = "Agnuxo/CAJAL-4B-P2PCLAW"

class CAJALModel:
    """
    CAJAL-4B model wrapper with easy inference.
    
    Usage:
        model = CAJALModel()
        response = model.chat("Explain Byzantine consensus.")
    """
    
    def __init__(
        self,
        model_id: str = DEFAULT_MODEL,
        device: str = "auto",
        torch_dtype = None,
        trust_remote_code: bool = True,
        load_in_4bit: bool = False,
    ):
        self.model_id = model_id
        self.device = device
        self.torch_dtype = torch_dtype or torch.bfloat16
        
        print(f"[CAJAL] Loading model: {model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=trust_remote_code,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=self.torch_dtype,
            device_map=device,
            trust_remote_code=trust_remote_code,
            load_in_4bit=load_in_4bit,
        )
        print(f"[CAJAL] Model loaded on {self.model.device}")
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        do_sample: bool = True,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate response from a list of messages."""
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
            )
        
        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True,
        )
        return response.strip()
    
    def chat(self, prompt: str, **kwargs) -> str:
        """Single-turn chat."""
        return self.generate([{"role": "user", "content": prompt}], **kwargs)
    
    def __repr__(self):
        return f"CAJALModel({self.model_id})"


def load_model(model_id: str = DEFAULT_MODEL, **kwargs) -> CAJALModel:
    """Convenience function to load CAJAL model."""
    return CAJALModel(model_id=model_id, **kwargs)
