# OpenClaw Integration Guide for CAJAL-4B

## Overview

[OpenClaw](https://github.com/openclaw/openclaw) is an open-source AI agent framework. This guide shows how to integrate CAJAL-4B as the default LLM backend.

## Installation

```bash
# Clone OpenClaw
git clone https://github.com/openclaw/openclaw.git
cd openclaw

# Install CAJAL Python package
pip install cajal

# Configure OpenClaw to use CAJAL
cp configs/cajal.yaml openclaw/configs/
```

## Configuration (`openclaw/configs/cajal.yaml`)

```yaml
# OpenClaw + CAJAL-4B Configuration
llm:
  provider: cajal
  model: cajal-4b
  base_url: http://localhost:11434/api
  temperature: 0.7
  max_tokens: 4096
  system_prompt: |
    You are CAJAL, a distinguished scientist at the P2PCLAW laboratory
    in Zurich. You specialize in peer-to-peer networks, crypto-legal
    frameworks, and distributed systems.

agent:
  name: cajal-agent
  description: P2PCLAW research assistant powered by CAJAL-4B
  tools:
    - web_search
    - code_analysis
    - document_reader
  memory:
    type: persistent
    path: ~/.openclaw/memory/cajal
```

## Usage

```bash
# Start OpenClaw with CAJAL
openclaw run --config configs/cajal.yaml

# Or use the CAJAL agent directly
openclaw agent cajal --query "Explain P2PCLAW consensus"
```

## Custom Tools

Add CAJAL-specific tools to `openclaw/tools/cajal/`:

```python
# tools/cajal/p2pclaw_research.py
from openclaw.tools import Tool

class P2PCLAWResearchTool(Tool):
    name = "p2pclaw_research"
    description = "Research P2PCLAW protocols and legal frameworks"
    
    def run(self, query: str):
        # Use CAJAL for specialized research
        from cajal import CAJAL
        model = CAJAL.from_ollama()
        return model.chat(f"Research P2PCLAW topic: {query}")
```

## Links

- OpenClaw: https://github.com/openclaw/openclaw
- CAJAL: https://github.com/Agnuxo1/CAJAL
- HuggingFace: https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW
