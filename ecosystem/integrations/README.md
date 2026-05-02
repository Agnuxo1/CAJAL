# CAJAL Integration Guides

Complete list of CAJAL-4B integrations for the P2PCLAW ecosystem.

## Code Editors & IDEs

| # | Platform | File | Status |
|---|----------|------|--------|
| 1 | **VS Code** (Continue.dev) | `continue.dev.md` | ✅ Ready |
| 2 | **VS Code** (CAJAL Extension) | `vscode-extension/` | ✅ Ready |
| 3 | **Cursor** | `cursor.md` | ✅ Ready |
| 4 | **Zed** | `zed.md` | ✅ Ready |
| 5 | **Windsurf** | `windsurf.md` | ✅ Ready |
| 6 | **JetBrains** | `continue.dev.md` | ✅ Via Continue |

## Chat Interfaces

| # | Platform | File | Status |
|---|----------|------|--------|
| 7 | **Ollama** (Native) | `ollama.md` | ✅ Ready |
| 8 | **Open WebUI** | `open-webui.md` | ✅ Ready |
| 9 | **LobeChat** | `lobechat.md` | ✅ Ready |
| 10 | **AnythingLLM** | `anythingllm.md` | ✅ Ready |
| 11 | **Chatbox** | `chatbox.md` | ✅ Ready |
| 12 | **ChatGPT (Custom GPT)** | `chatgpt-custom.md` | ✅ Ready |

## Desktop Apps

| # | Platform | File | Status |
|---|----------|------|--------|
| 13 | **LM Studio** | `lmstudio.md` | ✅ Ready |
| 14 | **Jan** | `jan.md` | ✅ Ready |
| 15 | **Claude Desktop** | `claude-desktop.md` | ✅ Ready |

## CLI Tools

| # | Platform | File | Status |
|---|----------|------|--------|
| 16 | **Aider** | `aider.md` | ✅ Ready |
| 17 | **OpenCode** | `opencode.md` | ✅ Ready |
| 18 | **CAJAL CLI** | `cli/cajal.py` | ✅ Ready |

## API Gateways

| # | Platform | File | Status |
|---|----------|------|--------|
| 19 | **LiteLLM / OpenRouter** | `openrouter.md` | ✅ Ready |
| 20 | **CAJAL API Bridge** | `api-bridge/bridge.py` | ✅ Ready |

## Specialized Tools

| # | Platform | File | Status |
|---|----------|------|--------|
| 21 | **text-generation-webui** | `text-generation-webui.md` | ✅ Ready |
| 22 | **KoboldCPP** | `koboldcpp.md` | ✅ Ready |
| 23 | **Supermaven** | `supermaven.md` | ✅ Ready |
| 24 | **Codex CLI** | `codex-cli.md` | ✅ Ready |

## Quick Reference

### Ollama is the Backend
All integrations connect through Ollama running CAJAL-4B:
```
Tool → Ollama API (localhost:11434) → CAJAL-4B GGUF
```

### CAJAL Bridge extends compatibility
For OpenAI-compatible tools:
```
Tool → CAJAL Bridge (localhost:8765) → Ollama → CAJAL-4B
```

### P2PCLAW Cloud Sync
```
CAJAL-4B (local) ←→ p2pclaw.com/silicon (cloud)
```

## Adding a New Integration

1. Create `{tool-name}.md` in this directory
2. Follow the template:
   - Prerequisites
   - Setup steps (numbered)
   - Configuration code blocks
   - Usage examples
   - Troubleshooting
3. Update this README table
4. Test locally before publishing
