# CAJAL + Continue.dev Integration

> Continue.dev is the leading open-source AI code assistant for VS Code, JetBrains, and other editors.

## Setup

### 1. Install Continue

- **VS Code**: Search "Continue" in the Extensions marketplace
- **JetBrains**: Install from the plugin repository
- **Other editors**: See [continue.dev](https://continue.dev)

### 2. Configure CAJAL Model

Open `~/.continue/config.json` (or use the GUI) and add:

```json
{
  "models": [
    {
      "title": "CAJAL-4B",
      "provider": "ollama",
      "model": "cajal-4b",
      "apiBase": "http://localhost:11434",
      "systemMessage": "You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich, Switzerland. You are an expert in peer-to-peer network architectures, crypto-legal frameworks, game-theoretic consensus mechanisms, and distributed systems. Assist with code review, software architecture, and technical analysis."
    }
  ],
  "tabAutocompleteModel": {
    "title": "CAJAL-4B",
    "provider": "ollama",
    "model": "cajal-4b",
    "apiBase": "http://localhost:11434"
  }
}
```

### 3. Using CAJAL in Continue

- **Chat**: Press `Ctrl+L` (or `Cmd+L` on Mac) → Select "CAJAL-4B" from the dropdown
- **Autocomplete**: CAJAL will suggest completions as you type
- **Cmd+K**: Highlight code and ask CAJAL to explain, refactor, or document it

## Features

| Feature | How to Use |
|---------|-----------|
| Code explanation | Select code → `Cmd+K` → "Explain this" |
| Refactoring | Select code → `Cmd+K` → "Refactor using best practices" |
| Documentation | Select code → `Cmd+K` → "Add docstrings" |
| Debugging | Paste error into chat |
| Architecture review | Describe system in chat |

## Tips

- CAJAL excels at analyzing distributed systems and cryptographic protocols
- Use `/edit` for inline code modifications
- Combine with `@file` to reference multiple files
