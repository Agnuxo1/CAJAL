from langchain.llms.base import LLM
from typing import Any, List, Mapping, Optional
import requests


class CAJALLangChain(LLM):
    """LangChain integration for CAJAL-4B-P2PCLAW.

    Usage:
        from cajal_p2pclaw.integrations.langchain import CAJALLangChain

        llm = CAJALLangChain(server_url="http://localhost:8000")
        result = llm.predict("Explain P2P consensus.")
    """

    server_url: str = "http://localhost:8000"
    model: str = "Agnuxo/CAJAL-4B-P2PCLAW"
    max_new_tokens: int = 512
    temperature: float = 0.7

    @property
    def _llm_type(self) -> str:
        return "cajal"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> str:
        res = requests.post(
            f"{self.server_url}/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "model": self.model,
                "max_new_tokens": self.max_new_tokens,
                "temperature": self.temperature,
            },
        )
        res.raise_for_status()
        return res.json()["response"]

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model, "server_url": self.server_url}
