from autogen.oai.client import OpenAIWrapper
import requests


class CAJALAutoGen:
    """AutoGen integration for CAJAL-4B-P2PCLAW.

    Usage:
        from cajal_p2pclaw.integrations.autogen import CAJALAutoGen

        client = CAJALAutoGen(server_url="http://localhost:8000")
        response = client.create(
            messages=[{"role": "user", "content": "Explain P2P consensus."}]
        )
    """

    def __init__(self, server_url: str = "http://localhost:8000", **kwargs):
        self.server_url = server_url
        self.model = "Agnuxo/CAJAL-4B-P2PCLAW"

    def create(self, messages: list, **kwargs) -> dict:
        res = requests.post(
            f"{self.server_url}/v1/chat/completions",
            json={
                "messages": messages,
                "model": self.model,
                "max_new_tokens": kwargs.get("max_new_tokens", 512),
                "temperature": kwargs.get("temperature", 0.7),
            },
        )
        res.raise_for_status()
        data = res.json()
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": data["response"],
                    }
                }
            ]
        }

    def message_retrieval(self, response: dict) -> list:
        return [choice["message"]["content"] for choice in response["choices"]]
