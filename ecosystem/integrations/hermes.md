# Hermes Agent Integration Guide for CAJAL-4B

## Overview

[Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research supports custom LLM backends. This guide configures Hermes to use CAJAL-4B.

## Configuration

Add to your Hermes config (`~/.hermes/config.yaml`):

```yaml
models:
  cajal-4b:
    provider: ollama
    base_url: http://localhost:11434
    model: cajal-4b
    temperature: 0.7
    max_tokens: 4096
    system_prompt: |
      You are CAJAL, a distinguished scientist at the P2PCLAW laboratory
      in Zurich, Switzerland. You are an expert in peer-to-peer network
      architectures, crypto-legal frameworks, game-theoretic consensus
      mechanisms, and distributed systems.

default_model: cajal-4b
```

## Environment Variables

```bash
export HERMES_MODEL=cajal-4b
export HERMES_OLLAMA_HOST=http://localhost:11434
```

## Usage

```bash
# Ask Hermes (uses CAJAL by default)
hermes "Explain zero-knowledge proofs in P2P networks"

# Use CAJAL specifically
hermes --model cajal-4b "Analyze this smart contract"
```

## Custom Agent

Create `~/.hermes/agents/cajal.yaml`:

```yaml
name: cajal
model: cajal-4b
system_prompt: |
  You are CAJAL, P2PCLAW research scientist...
tools:
  - code_analysis
  - web_search
  - document_reader
behavior:
  verbose: true
  show_thinking: true
```

## Links

- Hermes: https://github.com/NousResearch/hermes-agent
- CAJAL: https://github.com/Agnuxo1/CAJAL
