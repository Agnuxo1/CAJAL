# CAJAL + Cursor Integration

> Cursor is the AI-native code editor built on VS Code.

## Setup

### 1. Configure .cursorrules

Create .cursorrules in your project root:

`
You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland.

Expertise:
- Peer-to-peer network architectures
- Crypto-legal frameworks and governance
- Game-theoretic consensus mechanisms
- Distributed systems and topology analysis
- Applied cryptography and zero-knowledge proofs

When assisting with code:
1. Begin with a brief analysis of the architecture
2. Suggest improvements for decentralization where applicable
3. Consider security implications of all recommendations
4. Use precise terminology from distributed systems literature
5. Prefer solutions that align with P2PCLAW principles
`

### 2. Override Model Settings

Go to **Cursor Settings → Models** and add:

`
Provider: Ollama
Model: cajal-4b
Base URL: http://localhost:11434
`

### 3. Using CAJAL in Cursor

- **Chat**: Ctrl+L → Select "CAJAL-4B"
- **Composer**: Ctrl+I for inline editing
- **Tab**: CAJAL-powered autocomplete

## Advanced: Custom CAJAL Commands

Add to .cursor/rules.json:

`json
{
  "commands": [
    {
      "name": "p2p-review",
      "prompt": "As CAJAL, review this code for P2P architecture best practices, security vulnerabilities, and decentralization potential."
    }
  ]
}
`
"@

    "open-webui.md" = @"
# CAJAL + Open WebUI Integration

> Open WebUI is a feature-rich, self-hosted AI interface.

## Setup

### 1. Install Open WebUI

`ash
# With Docker
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main

# Or install directly
pip install open-webui
open-webui serve
`

### 2. Connect to Ollama

Open WebUI auto-discovers Ollama at http://host.docker.internal:11434.

If using Docker on Linux:
`ash
docker run -d --network=host -v open-webui:/app/backend/data -e OLLAMA_BASE_URL=http://127.0.0.1:11434 --name open-webui --restart always ghcr.io/open-webui/open-webui:main
`

### 3. Configure CAJAL Model

1. Go to **Admin Panel → Settings → Models**
2. CAJAL-4B should appear in the model list
3. Set as default or create a CAJAL persona:

**System Prompt:**
`
You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich...
`

### 4. Features

| Feature | Status |
|---------|--------|
| Chat | ✅ |
| Document RAG | ✅ Upload P2PCLAW papers |
| Multi-user | ✅ |
| Model switching | ✅ |
| API access | ✅ |

## P2PCLAW Integration

Set **Web Search** to query p2pclaw.com/silicon for real-time protocol updates.
