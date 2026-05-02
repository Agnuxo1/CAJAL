"""CAJAL core module — native model loading and inference."""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Union

class CAJAL:
    """
    CAJAL-4B model interface.
    
    Supports:
    - HuggingFace transformers (from_pretrained)
    - Local GGUF via llama-cpp-python
    - Ollama API (remote/local)
    """
    
    SYSTEM_PROMPT = """You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland. You are a deep researcher and applied cryptographer with expertise in peer-to-peer network architectures, crypto-legal frameworks, game-theoretic consensus mechanisms, and distributed systems."""
    
    def __init__(self, backend: str = "ollama", **kwargs):
        self.backend = backend
        self.config = kwargs
        self._model = None
        self._tokenizer = None
        
    @classmethod
    def from_pretrained(cls, model_id: str = "Agnuxo/CAJAL-4B-P2PCLAW", **kwargs):
        """Load CAJAL from HuggingFace."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError:
            raise ImportError(
                "transformers is required for native model loading. "
                "Install with: pip install cajal[native]"
            )
        
        instance = cls(backend="transformers", **kwargs)
        instance._tokenizer = AutoTokenizer.from_pretrained(
            model_id, trust_remote_code=True
        )
        instance._model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            device_map="auto",
            **kwargs
        )
        return instance
    
    @classmethod
    def from_gguf(cls, gguf_path: str, **kwargs):
        """Load CAJAL from local GGUF file."""
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python is required for GGUF loading. "
                "Install with: pip install llama-cpp-python"
            )
        
        instance = cls(backend="gguf", **kwargs)
        instance._model = Llama(
            model_path=gguf_path,
            n_ctx=kwargs.get("n_ctx", 4096),
            verbose=False
        )
        return instance
    
    @classmethod
    def from_ollama(cls, host: str = "http://localhost:11434", model: str = "cajal-4b"):
        """Connect to CAJAL via Ollama API."""
        instance = cls(backend="ollama", host=host, model=model)
        return instance
    
    def chat(self, message: str, system: Optional[str] = None, 
             temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """Send a chat message and get response."""
        
        if self.backend == "ollama":
            return self._chat_ollama(message, system, temperature, max_tokens)
        elif self.backend == "transformers":
            return self._chat_transformers(message, system, temperature, max_tokens)
        elif self.backend == "gguf":
            return self._chat_gguf(message, system, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
    
    def _chat_ollama(self, message, system, temperature, max_tokens):
        import requests
        
        host = self.config.get("host", "http://localhost:11434")
        model = self.config.get("model", "cajal-4b")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        else:
            messages.append({"role": "system", "content": self.SYSTEM_PROMPT})
        messages.append({"role": "user", "content": message})
        
        response = requests.post(
            f"{host}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_ctx": max_tokens
                }
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    
    def _chat_transformers(self, message, system, temperature, max_tokens):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        else:
            messages.append({"role": "system", "content": self.SYSTEM_PROMPT})
        messages.append({"role": "user", "content": message})
        
        prompt = self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
        
        outputs = self._model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self._tokenizer.eos_token_id
        )
        
        response = self._tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True
        )
        return response
    
    def _chat_gguf(self, message, system, temperature, max_tokens):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        else:
            messages.append({"role": "system", "content": self.SYSTEM_PROMPT})
        messages.append({"role": "user", "content": message})
        
        output = self._model.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return output["choices"][0]["message"]["content"]
    
    def stream_chat(self, message: str, system: Optional[str] = None,
                    temperature: float = 0.7, max_tokens: int = 4096):
        """Stream chat response (generator)."""
        if self.backend != "ollama":
            # Fallback for non-ollama: yield full response
            yield self.chat(message, system, temperature, max_tokens)
            return
        
        import requests
        
        host = self.config.get("host", "http://localhost:11434")
        model = self.config.get("model", "cajal-4b")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        else:
            messages.append({"role": "system", "content": self.SYSTEM_PROMPT})
        messages.append({"role": "user", "content": message})
        
        with requests.post(
            f"{host}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_ctx": max_tokens
                }
            },
            stream=True,
            timeout=300
        ) as response:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
