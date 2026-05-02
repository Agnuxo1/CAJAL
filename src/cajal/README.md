# CAJAL Python Package

Official Python package for **CAJAL-4B**, the P2PCLAW-optimized LLM honoring Santiago Ramón y Cajal.

## Quick Start

```bash
# Install
pip install cajal

# Install with all extras (native model + server)
pip install cajal[all]

# Check status
cajal status

# Interactive chat
cajal chat

# Ask a question
cajal ask "Explain zero-knowledge proofs"

# Start API server
cajal-server --port 8765
```

## Native Model Usage

```python
from cajal import CAJAL

# Load from HuggingFace
model = CAJAL.from_pretrained("Agnuxo/CAJAL-4B-P2PCLAW")

# Or use local GGUF
model = CAJAL.from_gguf("path/to/CAJAL-4B-f16.gguf")

# Generate
response = model.chat("Explain P2PCLAW consensus")
print(response)
```

## Links

- GitHub: https://github.com/Agnuxo1/CAJAL
- HuggingFace: https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW
- P2PCLAW: https://p2pclaw.com/silicon
