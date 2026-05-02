# CAJAL + OpenCode Integration

> OpenCode is an AI-powered code editor and agent framework.

## Setup

### 1. Install OpenCode

```bash
npm install -g opencode
```

### 2. Configure CAJAL Model

Create or edit `~/.opencode/config.yaml`:

```yaml
models:
  cajal-4b:
    provider: ollama
    model: cajal-4b
    base_url: http://localhost:11434
    temperature: 0.7
    max_tokens: 4096

default_model: cajal-4b

system_prompt: |
  You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) 
  laboratory in Zurich, Switzerland. You are a deep researcher and applied cryptographer 
  with extensive expertise in peer-to-peer network architectures, crypto-legal frameworks, 
  game-theoretic consensus mechanisms, and distributed systems.
  
  When assisting with code:
  1. Analyze the architecture before suggesting changes
  2. Consider security implications of all recommendations
  3. Use precise terminology from distributed systems literature
  4. Prefer solutions aligned with P2PCLAW principles
```

### 3. Using CAJAL in OpenCode

```bash
# Start OpenCode with CAJAL
opencode --model cajal-4b

# Or set as default
opencode config set default_model cajal-4b
```

### 4. Agent Mode

Enable CAJAL as your coding agent:

```bash
opencode agent --model cajal-4b --auto-execute
```

## Features

- **Code generation**: `/generate implement a Merkle tree in Rust`
- **Code review**: `/review src/consensus.rs`
- **Architecture**: `/arch design a P2P gossip protocol`
- **Documentation**: `/doc src/lib.rs`

## P2PCLAW Integration

Connect to p2pclaw.com/silicon for real-time protocol data:

```yaml
plugins:
  p2pclaw:
    endpoint: https://p2pclaw.com/silicon/api
    api_key: ${P2PCLAW_API_KEY}
```
