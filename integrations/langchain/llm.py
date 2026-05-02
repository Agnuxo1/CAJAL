"""
CAJAL LangChain Integration
https://github.com/langchain-ai/langchain

Installation:
    pip install cajal-p2pclaw langchain langchain-ollama

Usage:
    from cajal_p2pclaw.langchain import CAJALLLM
    llm = CAJALLLM(model="cajal")
    result = llm.invoke("Write an abstract about quantum computing")
"""

from typing import Any, List, Optional, Mapping
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
import requests

class CAJALLLM(LLM):
    """CAJAL Scientific Paper Generator as a LangChain LLM.
    
    Integrates CAJAL's paper generation capabilities into any LangChain chain or agent.
    """
    
    model: str = "cajal"
    """Ollama model name (default: cajal)"""
    
    ollama_host: str = "http://localhost:11434"
    """Ollama API host"""
    
    temperature: float = 0.3
    """Generation temperature"""
    
    max_tokens: int = 8192
    """Maximum tokens per generation"""
    
    system_prompt: str = """You are CAJAL (Cognitive Academic Journal Authoring Layer), a specialized scientific paper authoring assistant.

Generate publication-ready scientific papers with:
- Formal academic tone
- Proper structure (Abstract → Introduction → Methods → Results → Discussion → Conclusion → References)
- Real citations where possible
- Reproducible methodology
- Quantitative, evidence-based claims"""
    
    @property
    def _llm_type(self) -> str:
        return "cajal"
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> str:
        """Execute the LLM call."""
        
        full_prompt = f"{self.system_prompt}\n\nUser request: {prompt}\n\nGenerate a scientific response:"
        
        response = requests.post(
            f"{self.ollama_host}/api/generate",
            json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                    "num_ctx": 32768,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                    "stop": stop or ["<|endoftext|>", "</s>"]
                }
            },
            timeout=300
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise RuntimeError(f"Ollama error: {response.status_code} - {response.text}")
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> str:
        """Async version of _call."""
        return self._call(prompt, stop, run_manager, **kwargs)


# Convenience functions for common paper sections
def generate_abstract(topic: str, llm: Optional[CAJALLLM] = None) -> str:
    """Generate a paper abstract (150-250 words)."""
    llm = llm or CAJALLLM()
    prompt = f"Write a concise academic abstract (150-250 words) for a paper about: {topic}. Include background, methods, key results, and conclusion."
    return llm.invoke(prompt)

def generate_methods(topic: str, llm: Optional[CAJALLLM] = None) -> str:
    """Generate a detailed methodology section."""
    llm = llm or CAJALLLM()
    prompt = f"Write a detailed, reproducible methodology section for research on: {topic}. Include materials, procedures, parameters, datasets, and evaluation metrics."
    return llm.invoke(prompt)

def generate_full_paper(topic: str, llm: Optional[CAJALLLM] = None) -> str:
    """Generate a complete scientific paper."""
    llm = llm or CAJALLLM()
    prompt = f"Generate a complete scientific paper on: {topic}. Include: Abstract, Introduction, Related Work, Methodology, Results, Discussion, Conclusion, and References (minimum 8)."
    return llm.invoke(prompt)

def find_references(topic: str, llm: Optional[CAJALLLM] = None, n: int = 10) -> List[str]:
    """Find relevant academic references."""
    llm = llm or CAJALLLM()
    prompt = f"Suggest {n} relevant academic references for: {topic}. For each, provide: Author, Year, Title, Venue, DOI/arXiv ID."
    result = llm.invoke(prompt)
    # Parse references from result
    return [line.strip() for line in result.split('\n') if line.strip() and any(c.isdigit() for c in line)]


if __name__ == "__main__":
    # Demo usage
    print("🧪 CAJAL LangChain Integration Demo")
    print("=" * 50)
    
    llm = CAJALLLM()
    
    # Test abstract generation
    print("\n1. Abstract Generation:")
    abstract = generate_abstract("Neural architecture search for edge devices")
    print(abstract[:500] + "...")
    
    # Test full paper
    print("\n2. Full Paper Generation:")
    paper = generate_full_paper("Federated learning with differential privacy")
    print(paper[:1000] + "...")
