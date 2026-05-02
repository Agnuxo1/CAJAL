"""
LlamaIndex integration for CAJAL-4B.

Install:
    pip install llama-index cajal-cli

Usage:
    from cajal_llama import CajalLlamaLLM
    llm = CajalLlamaLLM()
    response = llm.complete("Explain P2PCLAW governance")
"""

from typing import Any, Dict, Optional, Sequence

from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_chat_callback, llm_completion_callback
from llama_index.core.llms.custom import CustomLLM
from llama_index.core.base.llms.generic_utils import chat_to_completion_decorator

import requests


class CajalLlamaLLM(CustomLLM):
    """LlamaIndex LLM for CAJAL-4B via Ollama.

    Example:
        .. code-block:: python

            from cajal_llama import CajalLlamaLLM
            from llama_index.core import Settings

            # Set as default LLM
            Settings.llm = CajalLlamaLLM()

            # Use in RAG pipeline
            from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
            documents = SimpleDirectoryReader("data").load_data()
            index = VectorStoreIndex.from_documents(documents)
            query_engine = index.as_query_engine()
            response = query_engine.query("Explain P2PCLAW")
    """

    model: str = "cajal-4b"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    top_p: float = 0.9
    num_ctx: int = 4096
    system_prompt: Optional[str] = None

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        if self.system_prompt is None:
            self.system_prompt = (
                "You are CAJAL, a distinguished scientist at the P2PCLAW "
                "laboratory in Zurich, Switzerland."
            )

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.num_ctx,
            num_output=4096,
            model_name=self.model,
            is_chat_model=True,
        )

    def _messages_to_ollama(self, messages: Sequence[ChatMessage]) -> list:
        ollama_msgs = []
        if self.system_prompt:
            ollama_msgs.append({"role": "system", "content": self.system_prompt})
        for msg in messages:
            ollama_msgs.append({"role": msg.role.value, "content": msg.content or ""})
        return ollama_msgs

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        ollama_messages = self._messages_to_ollama(messages)

        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_ctx": self.num_ctx,
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

        return ChatResponse(
            message=ChatMessage(role="assistant", content=content),
            raw=data,
        )

    @llm_chat_callback()
    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> CompletionResponseGen:
        ollama_messages = self._messages_to_ollama(messages)

        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": True,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_ctx": self.num_ctx,
            },
        }

        def gen() -> CompletionResponseGen:
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
                                yield CompletionResponse(
                                    delta=chunk,
                                    text=chunk,
                                    raw=data,
                                )
                        except json.JSONDecodeError:
                            continue

        return gen()

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        messages = [ChatMessage(role="user", content=prompt)]
        chat_response = self.chat(messages, **kwargs)
        return CompletionResponse(
            text=chat_response.message.content or "",
            raw=chat_response.raw,
        )

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        messages = [ChatMessage(role="user", content=prompt)]

        def gen() -> CompletionResponseGen:
            for chunk in self.stream_chat(messages, **kwargs):
                yield CompletionResponse(
                    delta=chunk.delta,
                    text=chunk.text,
                    raw=chunk.raw,
                )

        return gen()
