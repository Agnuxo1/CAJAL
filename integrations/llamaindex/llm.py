"""
CAJAL LlamaIndex Integration
https://github.com/run-llama/llama_index

Installation:
    pip install cajal-p2pclaw llama-index

Usage:
    from cajal_p2pclaw.llamaindex import CAJALQueryEngine, PaperGeneratorTool
    engine = CAJALQueryEngine()
    response = engine.query("Generate a paper on federated learning")
"""

from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.response_synthesizers import BaseSynthesizer
from llama_index.core.tools import FunctionTool
from llama_index.core.llms import LLM
from llama_index.llms.ollama import Ollama
from typing import Optional, List
import requests

class CAJALLLM(Ollama):
    """CAJAL-specific Ollama LLM configuration."""
    
    def __init__(
        self,
        model: str = "cajal",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.3,
        context_window: int = 32768,
        **kwargs
    ):
        super().__init__(
            model=model,
            base_url=base_url,
            temperature=temperature,
            context_window=context_window,
            **kwargs
        )


class CAJALQueryEngine(CustomQueryEngine):
    """Query engine for generating scientific papers."""
    
    llm: CAJALLLM
    
    def __init__(self, llm: Optional[CAJALLLM] = None):
        super().__init__(llm=llm or CAJALLLM())
    
    def custom_query(self, query_str: str) -> str:
        """Generate a paper based on the query."""
        
        system_prompt = """You are CAJAL, a scientific paper authoring assistant.
Generate a complete scientific paper based on the user's research topic.
Include: Abstract, Introduction, Related Work, Methodology, Results, Discussion, Conclusion, References."""

        full_prompt = f"{system_prompt}\n\nResearch topic: {query_str}\n\nGenerate the paper:"
        
        response = self.llm.complete(full_prompt)
        return str(response)


class PaperGeneratorTool:
    """LlamaIndex tool for paper generation."""
    
    def __init__(self, model: str = "cajal", ollama_host: str = "http://localhost:11434"):
        self.model = model
        self.ollama_host = ollama_host
    
    def generate_paper(self, topic: str, format: str = "markdown") -> str:
        """Generate a scientific paper."""
        response = requests.post(
            f"{self.ollama_host}/api/generate",
            json={
                "model": self.model,
                "prompt": f"Generate a complete scientific paper on: {topic}. Format: {format}",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_ctx": 32768
                }
            },
            timeout=300
        )
        return response.json().get("response", "")
    
    def generate_abstract(self, topic: str) -> str:
        """Generate a paper abstract."""
        return self.generate_paper(
            f"Write an abstract (150-250 words) for: {topic}",
            "abstract"
        )
    
    def generate_methods(self, topic: str) -> str:
        """Generate a methodology section."""
        return self.generate_paper(
            f"Write a detailed methodology section for: {topic}",
            "methods"
        )
    
    def find_references(self, topic: str, n: int = 10) -> List[str]:
        """Find relevant references."""
        result = self.generate_paper(
            f"List {n} relevant academic references for: {topic}. Include DOI/arXiv IDs.",
            "references"
        )
        return [line.strip() for line in result.split('\n') if line.strip()]
    
    def as_tool(self) -> FunctionTool:
        """Return as a LlamaIndex FunctionTool."""
        return FunctionTool.from_defaults(
            fn=self.generate_paper,
            name="cajal_paper_generator",
            description="Generate a scientific paper on any topic. Returns a complete paper with abstract, introduction, methods, results, discussion, conclusion, and references."
        )


if __name__ == "__main__":
    print("🧪 CAJAL LlamaIndex Integration Demo")
    print("=" * 50)
    
    # Query engine demo
    engine = CAJALQueryEngine()
    response = engine.query("Generate a paper on quantum error correction")
    print(f"\nQuery Engine Response ({len(response)} chars):")
    print(response[:500] + "...")
    
    # Tool demo
    tool = PaperGeneratorTool()
    paper = tool.generate_paper("Federated learning privacy mechanisms")
    print(f"\nTool Paper ({len(paper)} chars):")
    print(paper[:500] + "...")
