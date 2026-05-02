# CAJAL Browser Extension

Official browser extension for **CAJAL-4B**, the P2PCLAW-optimized LLM.

## Features

- **Popup Chat** — Quick access AI assistant in your browser toolbar
- **Page Summarization** — Summarize any webpage with one click
- **Text Explanation** — Select text and get instant explanations
- **Context Menu** — Right-click any selection to analyze with CAJAL
- **Sidebar Mode** — Persistent sidebar for extended conversations
- **Keyboard Shortcut** — `Ctrl+Shift+C` to open popup

## Installation

### Chrome / Edge / Brave

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `ecosystem/browser-extension` folder

### Firefox

1. Open `about:debugging`
2. Click "This Firefox" → "Load Temporary Add-on"
3. Select `manifest.json`

## Configuration

Click the settings icon in the popup or navigate to extension options to configure:
- Ollama host URL
- Model name (default: `cajal-4b`)
- Temperature and context length

## Requirements

- [Ollama](https://ollama.com) running locally
- CAJAL-4B model installed: `ollama create cajal-4b -f Modelfile`

## Links

- GitHub: https://github.com/Agnuxo1/CAJAL
- HuggingFace: https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW
- P2PCLAW: https://p2pclaw.com/silicon
