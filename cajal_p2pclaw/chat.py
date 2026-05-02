from typing import List, Dict, Optional
from .model import CAJALModel, DEFAULT_MODEL

SYSTEM_PROMPT_CAJAL = """You are CAJAL, a specialized scientific intelligence for the P2PCLAW decentralized research network. You have expertise in:
- Peer-to-peer network architectures
- Cryptographic protocols and zero-knowledge proofs  
- Distributed systems and Byzantine consensus
- Scientific paper generation and peer review
- Lean 4 formal verification
- Game-theoretic mechanism design

Provide rigorous, well-cited, and technically precise responses."""


class CAJALChat:
    """
    Stateful chat session with CAJAL.
    Maintains conversation history.
    """
    
    def __init__(
        self,
        model_id: str = DEFAULT_MODEL,
        system_prompt: Optional[str] = None,
        **model_kwargs
    ):
        self.model = CAJALModel(model_id=model_id, **model_kwargs)
        self.messages: List[Dict[str, str]] = []
        self.system_prompt = system_prompt or SYSTEM_PROMPT_CAJAL
    
    def send(self, message: str, **generate_kwargs) -> str:
        """Send a message and get response."""
        self.messages.append({"role": "user", "content": message})
        
        response = self.model.generate(
            messages=self.messages,
            system_prompt=self.system_prompt,
            **generate_kwargs
        )
        
        self.messages.append({"role": "assistant", "content": response})
        return response
    
    def reset(self):
        """Clear conversation history."""
        self.messages = []
    
    def history(self) -> List[Dict[str, str]]:
        """Get full conversation history."""
        return self.messages.copy()


def chat(prompt: str, model_id: str = DEFAULT_MODEL, **kwargs) -> str:
    """One-shot chat with CAJAL."""
    model = CAJALChat(model_id=model_id)
    return model.send(prompt, **kwargs)
