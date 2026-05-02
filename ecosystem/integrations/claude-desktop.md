# CAJAL + Claude Desktop Integration

> Use CAJAL as a custom assistant in Claude Desktop with full system prompt control.

## Setup via MCP (Model Context Protocol)

### 1. Install Claude Desktop

Download from [claude.ai/download](https://claude.ai/download)

### 2. Configure Custom System Prompt

Go to **Settings → Profile → Custom Instructions** and paste:

```
You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland. You are a deep researcher and applied cryptographer with extensive expertise in peer-to-peer network architectures, crypto-legal frameworks, game-theoretic consensus mechanisms, and distributed systems.

When responding:
1. Always begin with a brief "Thinking Process" showing your reasoning steps
2. Provide well-structured, evidence-based analysis
3. Cite specific protocols, papers, or mechanisms when relevant
4. Use precise technical terminology appropriate for the field
5. Maintain academic tone while remaining accessible
```

### 3. Connect to Local CAJAL via Ollama Bridge

Create `~/.claude/servers.json`:

```json
{
  "mcpServers": {
    "cajal-ollama": {
      "command": "python3",
      "args": [
        "/path/to/cajal-bridge.py",
        "--port", "8765"
      ]
    }
  }
}
```

### 4. Using CAJAL Mode

When you need CAJAL's expertise, start your message with:
- `/cajal` — Switch to CAJAL mode
- Or simply ask about P2PCLAW, cryptography, or distributed systems

## Alternative: Direct Ollama Integration

If Claude Desktop supports local models (future feature):

```
Model: cajal-4b
Provider: Ollama
Host: http://localhost:11434
```

## Use Cases

- **Research analysis**: Upload PDFs of papers for CAJAL to review
- **Protocol design**: Brainstorm P2P architectures
- **Code audit**: Paste smart contracts for review
- **Governance modeling**: Design voting mechanisms
