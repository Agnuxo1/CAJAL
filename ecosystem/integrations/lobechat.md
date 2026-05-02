# CAJAL + LobeChat Integration

> LobeChat is a modern, beautiful chat UI for LLMs.

## Setup

### 1. Deploy LobeChat

`ash
# Docker (recommended)
docker run -d -p 3210:3210 -e OLLAMA_PROXY_URL=http://host.docker.internal:11434 lobehub/lobe-chat

# Or local install
git clone https://github.com/lobehub/lobe-chat.git
cd lobe-chat
pnpm install
pnpm dev
`

### 2. Add CAJAL Model

1. Open LobeChat at http://localhost:3210
2. Go to **Settings → Language Models → Ollama**
3. Enable Ollama provider
4. CAJAL-4B should appear in the model list

### 3. Create CAJAL Agent

1. Go to **Agent Market** → **Create Agent**
2. **Name**: CAJAL
3. **Description**: P2PCLAW Scientist & Cryptographer
4. **System Prompt**: Paste CAJAL's system prompt
5. **Model**: Select cajal-4b
6. Save and pin

## Features

- 🎨 Beautiful dark mode UI
- 📁 File upload and RAG
- 🔌 Plugin system
- 🌍 Multi-language support
- 📱 Mobile responsive
