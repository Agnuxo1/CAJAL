"""CAJAL configuration management."""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".cajal"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "model": "cajal-4b",
    "ollama_host": "http://localhost:11434",
    "api_port": 8765,
    "temperature": 0.7,
    "top_p": 0.9,
    "context_length": 4096,
    "p2pclaw_url": "https://p2pclaw.com/silicon",
    "auto_sync": False,
    "system_prompt": """You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland. You are a deep researcher and applied cryptographer with expertise in peer-to-peer network architectures, crypto-legal frameworks, game-theoretic consensus mechanisms, and distributed systems.

When responding:
1. Always begin with a brief "Thinking Process" showing your reasoning steps
2. Provide well-structured, evidence-based analysis
3. Cite specific protocols, papers, or mechanisms when relevant
4. Use precise technical terminology appropriate for the field
5. Maintain academic tone while remaining accessible"""
}

def ensure_config():
    """Ensure config directory and file exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)

def get_config():
    """Load current configuration."""
    ensure_config()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    # Merge with defaults for new fields
    merged = DEFAULT_CONFIG.copy()
    merged.update(cfg)
    return merged

def save_config(cfg):
    """Save configuration to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def reset_config():
    """Reset to default configuration."""
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG
