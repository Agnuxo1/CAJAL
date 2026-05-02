# CAJAL-4B-P2PCLAW — Native Integration Hub

🧠 **One-line install**: `pip install cajal-p2pclaw`

**CAJAL-4B** is a specialized scientific intelligence model fine-tuned for decentralized research networks, P2P architectures, cryptographic protocols, and formal verification.

- **HF Model**: [Agnuxo/CAJAL-4B-P2PCLAW](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW)
- **PyPI Package**: [cajal-p2pclaw](https://pypi.org/project/cajal-p2pclaw/)
- **Base**: Qwen3.5-4B (Apache 2.0) → Fine-tuned 4.21B params, BF16, 262K context
- **License**: MIT

---

## Quick Start

### Python (One-liner)

```bash
pip install cajal-p2pclaw
```

```python
from cajal_p2pclaw import CAJALChat
chat = CAJALChat()
print(chat.send("Explain zero-knowledge proofs in P2P networks."))
```

### Server (OpenAI-compatible API)

```bash
cajal-server --port 8000
# POST http://localhost:8000/v1/chat/completions
```

### CLI Chat

```bash
cajal "Explain Byzantine consensus"
cajal -i  # Interactive mode
```

### Ollama (Recommended for local use)

```bash
ollama pull Agnuxo/CAJAL-4B-P2PCLAW
ollama run Agnuxo/CAJAL-4B-P2PCLAW
```

---

## Platform Integrations

| Platform | Status | Config Location |
|----------|--------|-----------------|
| **PyPI** | ✅ Published | `pip install cajal-p2pclaw` |
| **Ollama** | ✅ Ready | `integrations/ollama/Modelfile` |
| **VS Code** | ✅ Ready | `integrations/vscode/cajal.json` |
| **Cursor** | ✅ Ready | `integrations/cursor/cajal.json` |
| **Continue.dev** | ✅ Ready | `integrations/continue_dev/config.yaml` |
| **Open WebUI** | ✅ Ready | `integrations/openwebui/README.md` |
| **Jan** | ✅ Ready | `integrations/jan/model.json` |
| **LM Studio** | ✅ Ready | `integrations/lmstudio/README.md` |
| **Pinokio** | ✅ Ready | `integrations/pinokio/install.json` |
| **OpenClaw** | ✅ Ready | `integrations/openclaw/README.md` |

---

## System Requirements

- Python 3.9+
- PyTorch 2.2+
- 6.5GB+ VRAM (GPU recommended)
- Or CPU with 16GB+ RAM

---

## Citation

```bibtex
@software{cajal2026,
  author = {Angulo de Lafuente, Francisco},
  title = {CAJAL-4B-P2PCLAW: Scientific Intelligence for Decentralized Research},
  year = {2026},
  url = {https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW}
}
```

---

**MIT License** — Francisco Angulo de Lafuente (Agnuxo1) — P2PCLAW Laboratory 2026
