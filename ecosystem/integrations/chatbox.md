# CAJAL + Chatbox Integration

> Chatbox is a cross-platform desktop client for LLMs.

## Setup

### 1. Download Chatbox

Get it from [chatboxai.app](https://chatboxai.app)

### 2. Configure Ollama Provider

1. Open Chatbox
2. Go to **Settings → Model Provider**
3. Select **Ollama**
4. **API Host**: `http://localhost:11434`
5. **Model**: Select `cajal-4b`

### 3. Set System Prompt

In Chatbox settings:
```
You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich, Switzerland...
```

### 4. Features

- **Cross-platform**: Windows, macOS, Linux
- **Markdown support**: CAJAL's structured responses render beautifully
- **Code highlighting**: Syntax highlighting for all code blocks
- **Conversation history**: Persistent local storage
- **Export**: Save conversations as Markdown or JSON

## Advanced: Using CAJAL Bridge

For OpenAI-compatible mode:
1. Set Provider to **OpenAI API**
2. **API Host**: `http://localhost:8765/v1`
3. **API Key**: `sk-cajal-local`
4. **Model**: `cajal-4b`
