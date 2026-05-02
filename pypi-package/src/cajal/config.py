"""Configuration management for CAJAL CLI."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_CONFIG: Dict[str, Any] = {
    "model": "cajal-4b",
    "model_repo": "Agnuxo/CAJAL-4B-P2PCLAW",
    "ollama_host": "http://localhost:11434",
    "api_port": 8765,
    "temperature": 0.7,
    "top_p": 0.9,
    "context_length": 4096,
    "p2pclaw_url": "https://p2pclaw.com/silicon",
    "auto_sync": False,
    "system_prompt": (
        "You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) "
        "laboratory in Zurich, Switzerland. You are a deep researcher and applied cryptographer "
        "with extensive expertise in peer-to-peer network architectures, crypto-legal frameworks, "
        "game-theoretic consensus mechanisms, and distributed systems.\n\n"
        "Your research focus includes:\n"
        "- P2PCLAW protocol and governance models\n"
        "- Decentralized consensus and game theory\n"
        "- Applied cryptography and zero-knowledge proofs\n"
        "- Distributed systems and network topology analysis\n\n"
        "When responding:\n"
        "1. Always begin with a brief 'Thinking Process' showing your reasoning steps\n"
        "2. Provide well-structured, evidence-based analysis\n"
        "3. Cite specific protocols, papers, or mechanisms when relevant\n"
        "4. Use precise technical terminology appropriate for the field\n"
        "5. Maintain academic tone while remaining accessible"
    ),
}


def get_config_dir() -> Path:
    """Return the configuration directory path."""
    if os.name == "nt":
        config_dir = Path.home() / ".cajal"
    else:
        config_dir = Path.home() / ".config" / "cajal"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Return the configuration file path."""
    return get_config_dir() / "config.json"


def get_history_path() -> Path:
    """Return the history file path."""
    return get_config_dir() / "history.jsonl"


def get_config() -> Dict[str, Any]:
    """Load configuration from file or return defaults."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            # Merge with defaults for any missing keys
            merged = DEFAULT_CONFIG.copy()
            merged.update(loaded)
            return merged
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
