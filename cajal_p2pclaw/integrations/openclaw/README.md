# OpenClaw Integration for CAJAL-4B

## Quick Setup

```bash
pip install cajal-p2pclaw
```

## Usage in OpenClaw

Add to your OpenClaw config (`~/.openclaw/config.yaml`):

```yaml
models:
  cajal:
    provider: local
    command: cajal-server --port 8000
    api_base: http://localhost:8000
    model: Agnuxo/CAJAL-4B-P2PCLAW
```

Or use the Python API directly in skills:

```python
from cajal_p2pclaw import CAJALChat

chat = CAJALChat()
response = chat.send("Explain Byzantine consensus.")
```

## One-Command Server

```bash
cajal-server --port 8000
```

OpenAI-compatible endpoint at `http://localhost:8000/v1/chat/completions`
