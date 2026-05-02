# CAJAL Ecosystem

> **The complete CAJAL-4B deployment ecosystem for P2PCLAW**

## Overview

The CAJAL Ecosystem provides a complete, production-ready toolkit to deploy and use the CAJAL-4B fine-tuned model across 20+ platforms and tools. It includes:

- **One-click installer** (Windows, macOS, Linux)
- **CLI tool** (`cajal-cli`)
- **Web Chat App** (local-first, connects to Ollama)
- **VS Code Extension**
- **API Bridge** for `p2pclaw.com/silicon`
- **20+ integration guides** (Ollama, Continue.dev, Claude Desktop, Cursor, Zed, etc.)
- **Desktop App** (Electron-based)

## Quick Start

### Windows (PowerShell)
```powershell
irm https://p2pclaw.com/silicon/install.ps1 | iex
```

### Linux / macOS (Bash)
```bash
curl -fsSL https://p2pclaw.com/silicon/install.sh | bash
```

### Manual Installation
```bash
# Clone or download this ecosystem folder
cd ecosystem

# Install CLI tool
pip install -e cli/

# Install CAJAL-4B model into Ollama
./installer/setup-model.ps1  # or .sh
```

## Architecture

```
User -> [CLI / WebApp / VSCode / API] -> Ollama (local) -> CAJAL-4B GGUF
                                |
                                v
                     p2pclaw.com/silicon (cloud sync)
```

## Directory Structure

| Directory | Description |
|-----------|-------------|
| `installer/` | One-click installers for all platforms |
| `cli/` | Python CLI tool `cajal-cli` |
| `webapp/` | Standalone HTML/JS chat UI |
| `vscode-extension/` | VS Code extension source |
| `api-bridge/` | REST API bridge to p2pclaw.com/silicon |
| `integrations/` | Setup guides for 20+ platforms |
| `desktop-app/` | Electron desktop application |

## Integrations

1. **Ollama** — Local model server (primary backend)
2. **OpenCode** — AI coding agent integration
3. **Claude Desktop** — Custom system prompt + MCP
4. **Continue.dev** — VS Code / Cursor / JetBrains
5. **Zed Editor** — Zed assistant integration
6. **Cursor** — .cursorrules + model override
7. **Windsurf** — Cascade rules
8. **GitHub Copilot / Codex** — Custom instructions
9. **Aider** — Pair programming
10. **Supermaven** — Pro prompts
11. **Open WebUI** — Web interface
12. **LobeChat** — Modern chat UI
13. **AnythingLLM** — Document RAG
14. **Jan** — Local-first AI
15. **LM Studio** — Desktop GUI
16. **text-generation-webui** — Gradio UI
17. **KoboldCPP** — Storytelling
18. **Chatbox** — Cross-platform chat
19. **ChatGPT (Custom GPT)** — GPT builder instructions
20. **LiteLLM** — Unified API gateway

## License

MIT License — P2PCLAW Lab, Zurich
