# Windsurf Integration Guide for CAJAL-4B

## Overview

[Windsurf](https://windsurf.com) by Codeium is an AI-native IDE. This guide configures Windsurf to use CAJAL-4B.

## Configuration

Add to Windsurf settings (`~/.windsurf/settings.json`):

```json
{
  "windsurf.ai.model": "cajal-4b",
  "windsurf.ai.customEndpoint": {
    "url": "http://localhost:8765/v1/chat/completions",
    "apiKey": "dummy",
    "model": "cajal-4b"
  },
  "windsurf.ai.systemPrompt": "You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich. You are an expert in peer-to-peer networks, crypto-legal frameworks, and distributed systems."
}
```

## Start CAJAL Server

```bash
cajal-server --port 8765
```

## Usage

- **Cascade Chat**: Select CAJAL from the model dropdown
- **Inline Edit**: Select code → `Ctrl+I` → Ask CAJAL to modify
- **Command Palette**: `Ctrl+Shift+P` → "Windsurf: Ask CAJAL"

## Custom Commands

Create `~/.windsurf/commands.json`:

```json
{
  "commands": [
    {
      "name": "P2PCLAW Review",
      "prompt": "Review this code for P2PCLAW compliance, security vulnerabilities, and decentralized architecture patterns."
    },
    {
      "name": "Consensus Analysis",
      "prompt": "Analyze the consensus mechanism in this code for Byzantine fault tolerance, finality, and scalability."
    },
    {
      "name": "Crypto Audit",
      "prompt": "Audit this cryptographic implementation for side-channel attacks, weak parameters, and protocol compliance."
    }
  ]
}
```

## Links

- Windsurf: https://windsurf.com
- CAJAL: https://github.com/Agnuxo1/CAJAL
- P2PCLAW: https://p2pclaw.com/silicon
