# CAJAL Integration for Continue.dev

## Quick Setup

### 1. Install Continue.dev
[continue.dev](https://continue.dev) — Free, open-source AI coding assistant

### 2. Add CAJAL Commands

Create or edit `~/.continue/config.yaml`:

```yaml
customCommands:
  - name: "paper"
    description: "Generate scientific paper with CAJAL"
    prompt: |
      You are CAJAL, a scientific paper generator.
      
      Task: Generate a complete 7-section paper on: {input}
      
      Structure:
      1. Abstract (250 words)
      2. Introduction (500 words)
      3. Related Work (400 words, 8-10 citations)
      4. Methodology (600 words)
      5. Results (400 words)
      6. Discussion (500 words)
      7. Conclusion (250 words)
      
      Rules:
      - Use real arXiv citations
      - Academic tone
      - Include tribunal scoring after draft
      
  - name: "tribunal"
    description: "Peer-review current document"
    prompt: |
      You are a peer review tribunal with 3 independent reviewers.
      
      Review this text section by section:
      {input}
      
      Each reviewer must:
      1. Score 0-10
      2. Provide specific feedback
      3. Flag issues
      
      Consensus rule: 2/3 reviewers must score ≥7
```

### 3. Use Commands

In any editor with Continue.dev:
- `Ctrl+Shift+L` → type `/paper "quantum computing"`
- `Ctrl+Shift+L` → type `/tribunal` to review selected text

### 4. Ollama Model Setup

```bash
# Pull CAJAL model
ollama pull cajal-p2pclaw

# Or run directly
ollama run cajal-p2pclaw
```

### 5. Continue.dev Model Config

```yaml
models:
  - name: CAJAL
    provider: ollama
    model: cajal-p2pclaw
    apiBase: http://localhost:11434
```

## Features

| Feature | Status |
|---------|--------|
| Paper generation | ✅ Via `/paper` command |
| Peer review | ✅ Via `/tribunal` command |
| Real citations | ✅ arXiv integration |
| LaTeX output | 🚧 Coming soon |
| Local execution | ✅ 100% offline |

## Links

- CAJAL: https://github.com/Agnuxo1/CAJAL
- Paper: https://arxiv.org/pdf/2604.19792
- PyPI: https://pypi.org/project/cajal-p2pclaw/
- Continue.dev: https://continue.dev



---

**Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md) | **Sponsor:** [github.com/sponsors/Agnuxo1](https://github.com/sponsors/Agnuxo1)

**Roadmap:** [ROADMAP.md](ROADMAP.md)

## All Integrations

| Platform | Status | File |
|----------|--------|------|
| Ollama | ✅ Ready | `ollama-modelfile` |
| Continue.dev | ✅ Ready | `integrations/continue_dev/` |
| Jan | ✅ Ready | `integrations/jan/model.json` |
| Pinokio | ✅ Ready | `integrations/pinokio/install.json` |
| LM Studio | ✅ Ready | `integrations/lmstudio/README.md` |
| VS Code | ✅ Ready | `extensions/vscode/` |
| Chrome | ✅ Ready | `extensions/chrome/` |
