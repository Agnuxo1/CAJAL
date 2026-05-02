"""
LangChain integration for CAJAL-4B.

Install:
    pip install langchain cajal-cli

Usage:
    from cajal_langchain import CajalLLM
    llm = CajalLLM()
    result = llm.invoke("Explain P2PCLAW")
"""

from typing import Any, Dict, Iterator, List, Mapping, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk

import requests


class CajalLLM(LLM):
    """LangChain LLM wrapper for CAJAL-4B via Ollama.

    Example:
        .. code-block:: python

            from cajal_langchain import CajalLLM

            llm = CajalLLM(
                model="cajal-4b",
                base_url="http://localhost:11434",
                temperature=0.7,
            )

            # Simple invocation
            result = llm.invoke("Explain Byzantine fault tolerance")

            # In a chain
            from langchain import PromptTemplate
            template = PromptTemplate.from_template("Explain {topic}")
            chain = template | llm
            result = chain.invoke({"topic": "P2P governance"})
    """

    model: str = "cajal-4b"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    top_p: float = 0.9
    num_ctx: int = 4096
    system_prompt: Optional[str] = None

    @property
    def _llm_type(self) -> str:
        return "cajal-4b"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        messages = [{"role": "user", "content": prompt}]
        if self.system_prompt:
            messages.insert(0, {"role": "system", "content": self.system_prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_ctx": self.num_ctx,
                "stop": stop or [],
            },
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "")

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        messages = [{"role": "user", "content": prompt}]
        if self.system_prompt:
            messages.insert(0, {"role": "system", "content": self.system_prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_ctx": self.num_ctx,
                "stop": stop or [],
            },
        }

        with requests.post(
            f"{self.base_url}/api/chat", json=payload, stream=True, timeout=120
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        import json
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            chunk = data["message"]["content"]
                            yield GenerationChunk(text=chunk)
                            if run_manager:
                                run_manager.on_llm_new_token(chunk)
                    except json.JSONDecodeError:
                        continue


class CajalChatLLM(CajalLLM):
    """Chat-style LLM for LangChain with conversation history support."""

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._history: List[Dict[str, str]] = []

    def add_to_history(self, role: str, content: str) -> None:
        self._history.append({"role": role, "content": content})

    def clear_history(self) -> None:
        self._history = []

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        messages = list(self._history)
        if self.system_prompt and not any(m.get("role") == "system" for m in messages):
            messages.insert(0, {"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_ctx": self.num_ctx,
                "stop": stop or [],
            },
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")

        self.add_to_history("user", prompt)
        self.add_to_history("assistant", content)

        return content
