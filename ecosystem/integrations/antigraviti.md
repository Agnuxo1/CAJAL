# AntiGraviti Integration Guide for CAJAL-4B

## Overview

[AntiGraviti](https://github.com/antigraviti/antigraviti) is an AI-native development environment. This guide configures AntiGraviti to use CAJAL-4B.

## Configuration

Add to `~/.antigraviti/config.yaml`:

```yaml
llm:
  default: cajal-4b
  models:
    cajal-4b:
      provider: openai-compatible
      base_url: http://localhost:8765/v1
      model: cajal-4b
      api_key: dummy
      temperature: 0.7
      max_tokens: 4096
      system_prompt: |
        You are CAJAL, a distinguished scientist at the P2PCLAW laboratory
        in Zurich. You specialize in peer-to-peer networks, crypto-legal
        frameworks, and distributed systems.

agents:
  cajal-researcher:
    model: cajal-4b
    description: P2PCLAW research specialist
    tools:
      - file_reader
      - web_search
      - code_executor
    memory: persistent
```

## Start CAJAL API Server First

```bash
# Terminal 1: Start CAJAL API bridge
cajal-server --port 8765

# Terminal 2: Start AntiGraviti
antigraviti --agent cajal-researcher
```

## Usage in AntiGraviti

```
@cajal Explain the P2PCLAW governance model
@cajal Review this smart contract for vulnerabilities
@cajal Generate a consensus algorithm specification
```

## Environment Setup

```bash
export ANTIGRAVITI_DEFAULT_MODEL=cajal-4b
export ANTIGRAVITI_API_BASE=http://localhost:8765/v1
```

## Links

- AntiGraviti: https://github.com/antigraviti/antigraviti
- CAJAL: https://github.com/Agnuxo1/CAJAL
- P2PCLAW: https://p2pclaw.com/silicon
