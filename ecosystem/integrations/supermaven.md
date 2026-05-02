# CAJAL + Supermaven Integration

> Supermaven is an AI coding assistant with a 1M token context window.

## Setup

### 1. Install Supermaven

Install the plugin for your editor:
- VS Code: Search "Supermaven" in extensions
- JetBrains: Plugin marketplace
- Neovim: `nvim-treesitter` + Supermaven

### 2. Configure Custom Prompts

Supermaven doesn't directly support local models yet, but you can use the CAJAL Bridge:

Create a wrapper script that sends Supermaven requests to CAJAL:

```python
# cajal-supermaven-bridge.py
import requests

def get_cajal_completion(context, prompt):
    response = requests.post("http://localhost:8765/v1/completions", json={
        "model": "cajal-4b",
        "prompt": f"{context}\n\n{prompt}",
        "max_tokens": 256,
        "temperature": 0.7
    })
    return response.json()["choices"][0]["text"]
```

### 3. Alternative: Use CAJAL for Code Review

While Supermaven handles inline completion, use CAJAL for:
- Architecture reviews via `/review` command
- Security analysis of generated code
- Documentation generation

## Future Integration

Once Supermaven supports custom endpoints:
```
Provider: Custom
Endpoint: http://localhost:8765/v1
Model: cajal-4b
```

## Recommended Workflow

1. Use Supermaven for fast autocomplete
2. Use CAJAL (via Continue.dev or Aider) for deep analysis
3. Combine both for maximum productivity
