# CAJAL-4B Integration Ecosystem

> **Universal integration layer for CAJAL-4B** - Deploy the world's first scientific intelligence model for P2P systems across any platform.

[![PyPI](https://img.shields.io/pypi/v/cajal-cli.svg)](https://pypi.org/project/cajal-cli/)
[![HuggingFace](https://img.shields.io/badge/HF-Agnuxo/CAJAL--4B--P2PCLAW-orange)](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Named in honor of Santiago Ramon y Cajal**, the father of modern neuroscience.

---

## 30-Second Quick Start

```bash
# 1. Install Ollama
#    https://ollama.com/download

# 2. Pull CAJAL-4B
ollama pull Agnuxo/CAJAL-4B-P2PCLAW

# 3. Start chatting
ollama run Agnuxo/CAJAL-4B-P2PCLAW

# OR install the CLI
pip install cajal-cli
cajal chat
```

---

## What's Included

| Component | Description | Status |
|-----------|-------------|--------|
| **PyPI Package** (`cajal-cli`) | pip-installable CLI tool | Ready |
| **Python API** (`CajalClient`) | Programmatic access | Ready |
| **Universal Setup Script** | Auto-configure all platforms | Ready |
| **LangChain Integration** | Custom LLM wrapper | Ready |
| **LlamaIndex Integration** | RAG-compatible LLM | Ready |
| **CrewAI Integration** | Research tools for agents | Ready |
| **Pinokio Launcher** | One-click local deployment | Ready |
| **Open WebUI Tool** | Function calling in WebUI | Ready |
| **VS Code Extension** | IDE integration | Ready |
| **API Bridge** | OpenAI-compatible REST API | Ready |

---

## Platform Integrations

### IDEs & Editors

| Platform | Integration Method | Setup |
|----------|-------------------|-------|
| **VS Code** (Continue.dev) | Ollama provider | `python scripts/cajal-setup.py -p vscode` |
| **Cursor** | `.cursorrules` | `python scripts/cajal-setup.py -p cursor` |
| **Windsurf** | `.windsurfrules` | `python scripts/cajal-setup.py -p windsurf` |
| **Zed** | Settings JSON | `python scripts/cajal-setup.py -p zed` |
| **JetBrains** | Continue.dev plugin | Same as VS Code |

### Chat Interfaces

| Platform | Method |
|----------|--------|
| **Open WebUI** | Auto-detected via Ollama |
| **LobeChat** | Ollama provider |
| **AnythingLLM** | Ollama backend |
| **Chatbox** | Ollama provider |
| **Jan** | Import GGUF |

### CLI Tools

| Platform | Setup |
|----------|-------|
| **Aider** | `aider --model ollama/cajal-4b` |
| **OpenCode** | `python scripts/cajal-setup.py -p opencode` |
| **Codex CLI** | Set `OPENAI_BASE_URL=http://localhost:8765/v1` |
| **cajal-cli** | `pip install cajal-cli` |

### Desktop Apps

| Platform | Method |
|----------|--------|
| **LM Studio** | Import GGUF from HuggingFace |
| **Pinokio** | Use launcher.json |
| **GPT4All** | Import model |

### Framework Integrations

| Framework | Package | Install |
|-----------|---------|---------|
| **LangChain** | `cajal-langchain` | `pip install cajal-langchain` |
| **LlamaIndex** | `cajal-llamaindex` | `pip install cajal-llamaindex` |
| **CrewAI** | `cajal-crewai` | `pip install cajal-crewai` |

---

## Universal Setup

The fastest way to configure CAJAL across all your installed platforms:

```bash
# Download the setup script
curl -fsSL https://p2pclaw.com/setup.sh | bash

# Or manually:
python scripts/cajal-setup.py          # Auto-detect & configure all
python scripts/cajal-setup.py --check  # Check what's installed
python scripts/cajal-setup.py --list   # List supported platforms
```

---

## API Bridge (OpenAI-Compatible)

Any tool that supports the OpenAI API can use CAJAL:

```bash
# Start the bridge
cajal serve

# Or directly
python -m cajal.cli serve
```

Then configure your tool:
- **Base URL**: `http://localhost:8765/v1`
- **API Key**: any string (e.g., `sk-cajal-local`)
- **Model**: `cajal-4b`

---

## Python API

```python
from cajal import CajalClient

client = CajalClient()

# Simple chat
response = client.chat("Explain P2PCLAW governance")

# Streaming
for chunk in client.chat("Write a paper abstract on...", stream=True):
    print(chunk, end="")

# Check availability
if client.is_available():
    result = client.generate("Analyze this protocol")
```

---

## Directory Structure

```
CAJAL-integrations/
├── pypi-package/              # pip installable package
│   ├── src/cajal/             # Python source
│   │   ├── __init__.py
│   │   ├── cli.py             # Main CLI
│   │   ├── client.py          # Python API
│   │   └── config.py          # Configuration
│   ├── pyproject.toml
│   └── README.md
├── integrations/
│   ├── langchain/             # LangChain LLM wrapper
│   ├── llamaindex/            # LlamaIndex LLM
│   ├── crewai/                # CrewAI tools
│   ├── openclaw/              # OpenClaw connector
│   ├── vscode-extension/      # VS Code extension
│   ├── pinokio/               # Pinokio launcher
│   ├── open-webui/            # Open WebUI tool
│   └── ...
├── scripts/
│   ├── cajal-setup.py         # Universal setup
│   └── publish-pypi.sh        # PyPI publisher
└── README.md
```

---

## Publishing

### PyPI

```bash
# Set your token
export PYPI_TOKEN="your-api-token"

# Publish
bash scripts/publish-pypi.sh
```

### VS Code Marketplace

```bash
cd integrations/vscode-extension
npm install -g @vscode/vsce
vsce package
vsce publish
```

### HuggingFace

```python
from huggingface_hub import HfApi
api = HfApi()
api.upload_folder(
    folder_path="path/to/model",
    repo_id="Agnuxo/CAJAL-4B-P2PCLAW",
    repo_type="model",
)
```

---

## Model Information

| Property | Value |
|----------|-------|
| **Base Model** | Qwen/Qwen3.5-4B |
| **Parameters** | 4.2 Billion |
| **Context Length** | 262,144 tokens |
| **Fine-tuning** | LoRA r16 + QLoRA 4-bit |
| **Dataset** | 10,000 curated P2PCLAW examples |
| **Training Time** | ~13 hours (RTX 3090) |
| **Accuracy** | 98.95% |
| **Languages** | English, Spanish |
| **License** | MIT |

---

## Links

- **Model**: [huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW)
- **Platform**: [p2pclaw.com/silicon](https://p2pclaw.com/silicon)
- **PyPI**: [pypi.org/project/cajal-cli](https://pypi.org/project/cajal-cli)
- **GitHub**: [github.com/p2pclaw/cajal](https://github.com/p2pclaw/cajal)

---

*P2PCLAW Lab, Zurich. Licensed under MIT.*
