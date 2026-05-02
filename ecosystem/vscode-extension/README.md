# CAJAL — VS Code Extension

Official VS Code extension for **CAJAL-4B**, the P2PCLAW-optimized LLM honoring Santiago Ramón y Cajal.

## Features

- **Chat Panel** — Interactive AI assistant in a dedicated sidebar
- **Code Explanation** — Right-click any selected code to get detailed analysis
- **Ask CAJAL** — Quick questions via command palette
- **Customizable** — Configure Ollama host, model, temperature

## Installation

### From VSIX

1. Download `cajal-vscode-1.0.0.vsix` from [GitHub Releases](https://github.com/Agnuxo1/CAJAL/releases)
2. Open VS Code
3. Go to Extensions → "..." → "Install from VSIX"
4. Select the downloaded file

### From Marketplace

Search for "CAJAL" in the VS Code Extensions marketplace.

## Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| `CAJAL: Open Chat` | — | Open chat panel |
| `CAJAL: Ask` | — | Quick question input |
| `CAJAL: Explain Code` | — | Explain selected code |
| `CAJAL: Settings` | — | Open settings |

## Configuration

Open VS Code settings and search for "CAJAL":

- `cajal.ollamaHost`: Ollama server URL (default: `http://localhost:11434`)
- `cajal.model`: Model name (default: `cajal-4b`)
- `cajal.temperature`: Generation temperature (default: `0.7`)
- `cajal.maxTokens`: Maximum context length (default: `4096`)

## Requirements

- [Ollama](https://ollama.com) running locally
- CAJAL-4B model installed

## Links

- GitHub: https://github.com/Agnuxo1/CAJAL
- HuggingFace: https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW
- P2PCLAW: https://p2pclaw.com/silicon
