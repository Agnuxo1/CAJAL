# CAJAL — P2PCLAW-Optimized LLM

> **CAJAL-4B: A fine-tuned Qwen3.5-4B model specialized in peer-to-peer network architectures, crypto-legal frameworks, game-theoretic consensus mechanisms, and distributed systems. Named in honor of Santiago Ramón y Cajal, the father of modern neuroscience, whose discovery of neural networks mirrors the decentralized systems CAJAL studies.**

[![HuggingFace](https://img.shields.io/badge/HuggingFace-Agnuxo/CAJAL--4B--P2PCLAW-orange)](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW)
[![GitHub](https://img.shields.io/badge/GitHub-Agnuxo1/CAJAL-blue)](https://github.com/Agnuxo1/CAJAL)
[![License](https://img.shields.io/badge/License-MIT-green)](legal/NOTICE)
[![PyPI](https://img.shields.io/badge/PyPI-cajal-blueviolet)](https://pypi.org/project/cajal/)

---

## Quick Start

### Install

```bash
# Via pip (includes CLI + server)
pip install cajal

# With all extras (native model loading + server)
pip install cajal[all]
```

### Use

```bash
# Check status
cajal status

# Interactive chat
cajal chat

# Ask a question
cajal ask "Explain Byzantine fault tolerance in P2P networks"

# Start OpenAI-compatible API server
cajal-server --port 8765
```

### Python API

```python
from cajal import CAJAL

# Via Ollama (recommended)
model = CAJAL.from_ollama()
print(model.chat("Explain P2PCLAW consensus"))

# Via HuggingFace
model = CAJAL.from_pretrained("Agnuxo/CAJAL-4B-P2PCLAW")
print(model.chat("Explain P2PCLAW consensus"))
```

---

## Model Details

| Attribute | Value |
|-----------|-------|
| **Name** | CAJAL-4B-P2PCLAW |
| **Base Model** | Qwen3.5-4B |
| **Architecture** | Qwen3_5ForCausalLM (hybrid linear_attention + self_attn) |
| **Parameters** | 4 billion (3.81B active) |
| **Context** | 4,096 tokens |
| **Fine-tuning** | LoRA (r=16, α=32, dropout=0.05) |
| **Dataset** | 10,000 P2PCLAW examples |
| **Training** | 3 epochs, ~12.8 hours on RTX 3090 |
| **Final Loss** | 0.03192 |
| **Accuracy** | 98.95% |
| **GGUF** | CAJAL-4B-f16.gguf (8.4 GB) |

---

## Ecosystem

CAJAL is available through **20+ integrations** across every major platform:

### Command Line & APIs
- **PyPI** — `pip install cajal`
- **Ollama** — `ollama create cajal-4b -f Modelfile`
- **OpenAI-compatible API** — `cajal-server --port 8765`

### IDEs & Editors
- **VS Code** — Extension with chat panel, code explain, inline suggestions
- **Cursor** — AI-native editor integration via OpenAI-compatible endpoint
- **Windsurf** — Codeium IDE with CAJAL custom model
- **Kilocode** — Coding assistant with P2PCLAW review commands
- **Zed** — High-performance editor integration

### Local LLM Platforms
- **LM Studio** — Desktop GUI with tool plugins
- **Jan** — Open-source ChatGPT alternative
- **AnythingLLM** — Private document chat
- **GPT4All** — Local LLM runner
- **text-generation-webui** — Gradio web UI
- **KoboldCPP** — Story-writing focused

### Agent Frameworks
- **OpenClaw** — P2PCLAW agent framework
- **Hermes** — Nous Research agent
- **AntiGraviti** — AI-native development environment
- **CrewAI** — Multi-agent orchestration
- **LangChain** — LLM application framework
- **AutoGen** — Microsoft multi-agent framework
- **LlamaIndex** — Data framework for LLMs

### Browser & Desktop
- **Browser Extension** — Chrome/Firefox/Edge with popup, sidebar, context menu
- **Desktop Tray App** — Cross-platform system tray (Windows/Linux/macOS)
- **Pinokio** — One-click AI app launcher

### Cloud & API
- **HuggingFace** — `Agnuxo/CAJAL-4B-P2PCLAW`
- **OpenRouter** — Unified AI API
- **P2PCLAW Silicon** — https://p2pclaw.com/silicon

---

## Directory Structure

```
CAJAL/
├── src/cajal/              # PyPI package source
│   ├── __init__.py         # Package entry
│   ├── core.py             # Native model loading (HF/GGUF/Ollama)
│   ├── cli.py              # Command-line interface
│   ├── server.py           # OpenAI-compatible API server
│   ├── config.py           # Configuration management
│   └── desktop.py          # System tray application
├── ecosystem/
│   ├── cli/                # Standalone CLI scripts
│   ├── vscode-extension/   # VS Code extension
│   ├── browser-extension/  # Chrome/Firefox/Edge extension
│   ├── webapp/             # Standalone web chat UI
│   ├── api-bridge/         # Flask API bridge
│   ├── installer/          # Windows/Linux/macOS installers
│   ├── integrations/       # 20+ platform integration guides
│   └── pinokio/            # Pinokio launcher JSON
├── scripts/                # Training and utility scripts
├── datasets/               # Training datasets
├── outputs/                # Model outputs
├── legal/                  # LICENSE, NOTICE, Model Card
└── pyproject.toml          # PyPI package configuration
```

---

## Training Pipeline

```
Phase 0: Collect Ecosystem          ⏱️ 30 min - 2 hours
├── Download 20+ repositories
├── Collect P2PCLAW papers and skills
└── Gather FrontierMath resources

Phase 1: Prepare Dataset            ⏱️ 30 minutes
├── Download papers from p2pclaw.com
├── Convert to conversation format
└── Build training dataset

Phase 2: Train Model                ⏱️ 2-6 hours
├── Load base model (Qwen3.5-4B)
├── Apply LoRA fine-tuning
├── Export to GGUF
└── Create Ollama Modelfile

Phase 3: Deploy & Publish           ⏱️ 1-2 hours
├── Test locally with Ollama
├── Publish to HuggingFace
├── Build ecosystem integrations
└── Release packages
```

---

## Integration Guides

Detailed setup instructions for each platform are in [`ecosystem/integrations/`](ecosystem/integrations/):

| Platform | File | Description |
|----------|------|-------------|
| Ollama | [`ollama.md`](ecosystem/integrations/ollama.md) | Local inference |
| VS Code | [`vscode-extension/`](ecosystem/vscode-extension/) | IDE extension |
| Continue.dev | [`continue.dev.md`](ecosystem/integrations/continue.dev.md) | Open-source copilot |
| Cursor | [`cursor.md`](ecosystem/integrations/cursor.md) | AI-native editor |
| LM Studio | [`lmstudio.md`](ecosystem/integrations/lmstudio.md) | Desktop GUI |
| OpenClaw | [`openclaw.md`](ecosystem/integrations/openclaw.md) | Agent framework |
| Hermes | [`hermes.md`](ecosystem/integrations/hermes.md) | Nous Research agent |
| Kilocode | [`kilocode.md`](ecosystem/integrations/kilocode.md) | Coding assistant |
| AntiGraviti | [`antigraviti.md`](ecosystem/integrations/antigraviti.md) | Dev environment |
| Codex CLI | [`codex-cli.md`](ecosystem/integrations/codex-cli.md) | OpenAI Codex |
| Pinokio | [`pinokio/`](ecosystem/pinokio/) | One-click launcher |
| And 12 more... | [`integrations/`](ecosystem/integrations/) | See directory |

---

## License

This project is licensed under the **MIT License**. See [`legal/NOTICE`](legal/NOTICE) for details.

The base model **Qwen3.5-4B** is provided by Alibaba Cloud under the Qwen License.

---

**In memory of Santiago Ramón y Cajal** (1852–1934)

*"The brain is a world consisting of a number of unexplored continents and great stretches of unknown territory."*

---

**Copyright 2026 P2PCLAW Research**

- GitHub: https://github.com/Agnuxo1/CAJAL
- HuggingFace: https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW
- P2PCLAW: https://p2pclaw.com/silicon
