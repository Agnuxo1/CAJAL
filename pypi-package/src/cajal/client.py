"""CAJAL client for programmatic access."""

import json
import uuid
from typing import Any, Dict, Iterator, List, Optional, Union

import requests

from .config import get_config


class CajalClient:
    """Client for interacting with CAJAL-4B via Ollama."""

    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        context_length: Optional[int] = None,
    ):
        cfg = get_config()
        self.host = (host or cfg.get("ollama_host", "http://localhost:11434")).rstrip("/")
        self.model = model or cfg.get("model", "cajal-4b")
        self.system_prompt = system_prompt or cfg.get("system_prompt", "")
        self.temperature = temperature if temperature is not None else cfg.get("temperature", 0.7)
        self.top_p = top_p if top_p is not None else cfg.get("top_p", 0.9)
        self.context_length = context_length if context_length is not None else cfg.get("context_length", 4096)
        self._session: Optional[List[Dict[str, str]]] = None

    def _build_messages(self, prompt: str) -> List[Dict[str, str]]:
        """Build message list with system prompt and conversation history."""
        messages: List[Dict[str, str]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if self._session:
            messages.extend(self._session)
        messages.append({"role": "user", "content": prompt})
        return messages

    def chat(self, prompt: str, stream: bool = False) -> Union[str, Iterator[str]]:
        """Send a chat message to CAJAL."""
        messages = self._build_messages(prompt)
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_ctx": self.context_length,
            },
        }

        if stream:
            return self._chat_streaming(payload, prompt)

        response = requests.post(
            f"{self.host}/api/chat",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        self._add_to_session(prompt, content)
        return content

    def _chat_streaming(self, payload: Dict[str, Any], prompt: str) -> Iterator[str]:
        """Stream chat response."""
        full_content = []
        with requests.post(
            f"{self.host}/api/chat",
            json=payload,
            stream=True,
            timeout=120,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            chunk = data["message"]["content"]
                            full_content.append(chunk)
                            yield chunk
                    except json.JSONDecodeError:
                        continue
        self._add_to_session(prompt, "".join(full_content))

    def _add_to_session(self, user_msg: str, assistant_msg: str) -> None:
        """Add exchange to conversation session."""
        if self._session is None:
            self._session = []
        self._session.append({"role": "user", "content": user_msg})
        self._session.append({"role": "assistant", "content": assistant_msg})

    def clear_session(self) -> None:
        """Clear conversation history."""
        self._session = None

    def is_available(self) -> bool:
        """Check if Ollama with CAJAL is available."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return any(self.model in m for m in models)
            return False
        except requests.exceptions.ConnectionError:
            return False

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text from a prompt (simpler interface)."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": max_tokens or self.context_length,
            },
        }

        response = requests.post(
            f"{self.host}/api/chat",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "")

    @staticmethod
    def install_model(model_repo: str = "Agnuxo/CAJAL-4B-P2PCLAW") -> bool:
        """Install CAJAL model from HuggingFace via Ollama."""
        try:
            import subprocess
            result = subprocess.run(
                ["ollama", "pull", model_repo],
                capture_output=True,
                text=True,
                timeout=600,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
