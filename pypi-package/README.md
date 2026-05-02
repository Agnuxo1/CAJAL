# CAJAL-4B CLI

> **The complete command-line interface for CAJAL-4B**, a specialized scientific intelligence model for peer-to-peer systems, cryptography, and decentralized governance.

[![PyPI](https://img.shields.io/pypi/v/cajal-cli.svg)](https://pypi.org/project/cajal-cli/)
[![Python](https://img.shields.io/pypi/pyversions/cajal-cli.svg)](https://pypi.org/project/cajal-cli/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![HuggingFace](https://img.shields.io/badge/HF-Agnuxo/CAJAL--4B--P2PCLAW-orange)](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW)

Named in honor of **Santiago Ramon y Cajal** (1852-1934), the father of modern neuroscience, whose pioneering work on neural architectures inspires our mission to understand decentralized systems.

---

## Quick Start

### Install

```bash
pip install cajal-cli
```

### Install the Model

```bash
# Install Ollama first: https://ollama.com/download

# Pull CAJAL-4B
cajal install

# Or directly with Ollama
ollama pull Agnuxo/CAJAL-4B-P2PCLAW
```

### Start Chatting

```bash
# Interactive chat
cajal chat

# Single question
cajal ask "Explain the Byzantine Generals Problem in P2P networks"

# Check status
cajal status
```

---

## Features

- **Interactive Chat** - Real-time streaming chat with CAJAL-4B
- **OpenAI-Compatible API** - Start a local API bridge for any OpenAI-compatible tool
- **One-Command Install** - `cajal install` pulls the model automatically
- **Web Chat UI** - Launch the web interface with `cajal webapp`
- **Persistent History** - Conversations saved locally
- **Python API** - Use `CajalClient` in your Python scripts

---

## Commands

| Command | Description |
|---------|-------------|
| `cajal status` | Check Ollama and CAJAL model status |
| `cajal install` | Install CAJAL-4B into Ollama |
| `cajal chat` | Start interactive chat session |
| `cajal ask "..."` | Ask a single question |
| `cajal serve` | Start OpenAI-compatible API bridge |
| `cajal list` | List available Ollama models |
| `cajal webapp` | Launch web chat UI |
| `cajal config` | Edit configuration |

---

## Python API

```python
from cajal import CajalClient

# Create client (auto-discovers config)
client = CajalClient()

# Check availability
if client.is_available():
    # Chat
    response = client.chat("Explain P2PCLAW governance")
    print(response)

    # Streaming
    for chunk in client.chat("Write an abstract on consensus", stream=True):
        print(chunk, end="")

    # Simple generation
    result = client.generate("Summarize zero-knowledge proofs")
```

---

## Configuration

Config file at `~/.cajal/config.json`:

```json
{
  "model": "cajal-4b",
  "ollama_host": "http://localhost:11434",
  "temperature": 0.7,
  "top_p": 0.9,
  "context_length": 4096
}
```

---

## API Bridge

Start an OpenAI-compatible API server:

```bash
cajal serve --port 8765
```

Then use with any OpenAI-compatible tool:

```bash
curl http://localhost:8765/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "cajal-4b",
    "messages": [{"role": "user", "content": "Hello CAJAL"}]
  }'
```

---

## About CAJAL-4B

| Property | Value |
|----------|-------|
| Base Model | Qwen/Qwen3.5-4B |
| Parameters | 4.2 Billion |
| Context Length | 262,144 tokens |
| Fine-tuning | LoRA r16 + QLoRA 4-bit |
| Training Data | 10,000 curated P2PCLAW examples |
| Languages | English, Spanish |
| License | MIT |

### Core Competencies

- Peer-to-peer network architectures
- Crypto-legal frameworks and governance
- Game-theoretic consensus mechanisms
- Applied cryptography and zero-knowledge proofs
- Distributed systems analysis
- Scientific paper generation

---

## Links

- **Platform**: [p2pclaw.com/silicon](https://p2pclaw.com/silicon)
- **Model**: [huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW)
- **GitHub**: [github.com/p2pclaw/cajal-cli](https://github.com/p2pclaw/cajal-cli)
- **P2PCLAW**: [p2pclaw.com](https://p2pclaw.com)

---

*P2PCLAW Lab, Zurich. Licensed under MIT.*
