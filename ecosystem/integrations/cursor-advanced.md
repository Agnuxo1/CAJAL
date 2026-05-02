# Cursor Integration Guide for CAJAL-4B

## Overview

[Cursor](https://cursor.com) is an AI-native code editor. This guide configures Cursor to use CAJAL-4B as a custom model.

## Configuration

1. Open Cursor Settings (`Ctrl+,`)
2. Go to **Models** → **Add Model**
3. Add OpenAI-compatible endpoint:

```
Base URL: http://localhost:8765/v1
API Key: dummy (any value)
Model: cajal-4b
```

Or edit `~/.cursor/settings.json`:

```json
{
  "cursor.ai.model": "cajal-4b",
  "cursor.ai.openaiBaseUrl": "http://localhost:8765/v1",
  "cursor.ai.openaiKey": "dummy",
  "cursor.ai.customModels": [
    {
      "name": "cajal-4b",
      "provider": "openai-compatible",
      "baseUrl": "http://localhost:8765/v1",
      "apiKey": "dummy"
    }
  ]
}
```

## Start CAJAL Server

```bash
# Terminal
cajal-server --port 8765
```

## Usage

- **Chat**: `Ctrl+L` → Select "cajal-4b" from model dropdown
- **Tab Completion**: Cursor uses CAJAL for inline suggestions
- **Code Review**: Select code → Right-click → "Review with CAJAL"
- **@ Commands**:
  - `@cajal Explain this function`
  - `@cajal Find security issues`
  - `@cajal Refactor for P2P architecture`

## Custom Rules

Create `.cursorrules` in your project root:

```
You are CAJAL, P2PCLAW research scientist.
When writing code:
- Prioritize decentralization and fault tolerance
- Use cryptographic best practices
- Consider Byzantine fault tolerance
- Document network topology assumptions
- Follow P2PCLAW protocol standards
```

## Cursor Marketplace Plugin (Future)

To publish as a Cursor plugin:
1. Create `.cursor/skills/cajal.json`:

```json
{
  "name": "cajal",
  "version": "1.0.0",
  "description": "P2PCLAW AI Assistant",
  "skills": [
    {
      "name": "p2pclaw-review",
      "description": "Review code for P2PCLAW compliance"
    },
    {
      "name": "consensus-analysis",
      "description": "Analyze consensus mechanisms"
    }
  ]
}
```

## Links

- Cursor: https://cursor.com
- CAJAL: https://github.com/Agnuxo1/CAJAL
- P2PCLAW: https://p2pclaw.com/silicon
