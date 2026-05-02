# Kilocode Integration Guide for CAJAL-4B

## Overview

[Kilocode](https://github.com/kilocode/kilocode) is a coding assistant that supports custom LLM backends. This guide configures Kilocode to use CAJAL-4B for code analysis.

## VS Code Extension Setup

1. Install the Kilocode extension in VS Code
2. Open Settings (`Ctrl+,`)
3. Search for "Kilocode"
4. Set the following:

```json
{
  "kilocode.model": "cajal-4b",
  "kilocode.provider": "ollama",
  "kilocode.ollamaBaseUrl": "http://localhost:11434",
  "kilocode.temperature": 0.7,
  "kilocode.maxTokens": 4096
}
```

## Configuration File

Create `~/.kilocode/config.json`:

```json
{
  "models": [
    {
      "name": "cajal-4b",
      "provider": "ollama",
      "baseUrl": "http://localhost:11434",
      "modelId": "cajal-4b",
      "temperature": 0.7,
      "maxTokens": 4096,
      "systemPrompt": "You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich. You are an expert in peer-to-peer network architectures, crypto-legal frameworks, and distributed systems. Provide rigorous, well-structured code analysis with evidence-based reasoning."
    }
  ],
  "defaultModel": "cajal-4b"
}
```

## Usage

- Select code and press `Ctrl+Shift+K` to ask CAJAL
- Use inline chat with `/explain` to get CAJAL's analysis
- Use `/refactor` to get improvement suggestions

## Custom Commands

Add to `~/.kilocode/commands.json`:

```json
{
  "commands": [
    {
      "name": "p2pclaw-review",
      "description": "Review code for P2PCLAW compliance",
      "prompt": "Review this code for compliance with P2PCLAW protocols, security best practices, and decentralized architecture patterns. Identify potential vulnerabilities and suggest improvements."
    },
    {
      "name": "consensus-analysis",
      "description": "Analyze consensus mechanism",
      "prompt": "Analyze the consensus mechanism in this code. Evaluate its Byzantine fault tolerance, finality, and scalability properties."
    }
  ]
}
```

## Links

- Kilocode: https://github.com/kilocode/kilocode
- CAJAL: https://github.com/Agnuxo1/CAJAL
