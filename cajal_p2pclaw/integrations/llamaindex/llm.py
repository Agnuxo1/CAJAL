from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback
import requests


class CAJALLlamaIndex(CustomLLM):
    """LlamaIndex integration for CAJAL-4B-P2PCLAW.

    Usage:
        from cajal_p2pclaw.integrations.llamaindex import CAJALLlamaIndex

        llm = CAJALLlamaIndex(server_url="http://localhost:8000")
        response = llm.complete("Summarize this paper on P2P networks.")
    """

    server_url: str = "http://localhost:8000"
    model: str = "Agnuxo/CAJAL-4B-P2PCLAW"
    max_new_tokens: int = 512
    temperature: float = 0.7

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=262000,
            num_output=self.max_new_tokens,
            model_name=self.model,
        )

    @llm_completion_callback()
    def complete(self, query: str, **kwargs) -> CompletionResponse:
        res = requests.post(
            f"{self.server_url}/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": query}],
                "model": self.model,
                "max_new_tokens": self.max_new_tokens,
                "temperature": self.temperature,
            },
        )
        res.raise_for_status()
        return CompletionResponse(text=res.json()["response"])

    @llm_completion_callback()
    def stream_complete(self, query: str, **kwargs):
        # Streaming implementation can be added here
        yield self.complete(query, **kwargs)
