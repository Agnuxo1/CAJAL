## CAJAL Integration for Continue.dev

Run CAJAL paper generation directly inside Continue.dev with custom `.prompt` files.

### Setup

1. Install Continue.dev: https://continue.dev
2. Add this to your `config.yaml`:

```yaml
customCommands:
  - name: "paper"
    description: "Generate a scientific paper with CAJAL"
    prompt: |
      You are CAJAL, a scientific paper generator. 
      Generate a 7-section paper on: {input}
      
      Sections: Abstract, Introduction, Related Work, Methodology, Results, Discussion, Conclusion.
      Include real arXiv citations.
      After drafting, score each section 0-10 as a peer reviewer.
      Rewrite sections scoring <7. Max 3 iterations.
    
  - name: "tribunal"
    description: "Peer-review an existing paper"
    prompt: |
      You are a peer review tribunal with 3 independent reviewers.
      Review this paper section by section:
      {input}
      
      Each reviewer scores 0-10 with detailed feedback.
      Flag sections needing revision.
```

3. Use `/paper "quantum computing"` in any chat
4. Or `/tribunal` to review existing text

### Model Configuration

```yaml
models:
  - name: CAJAL
    provider: ollama
    model: cajal-p2pclaw
```

### Links
- CAJAL Repo: https://github.com/Agnuxo1/CAJAL
- PyPI: https://pypi.org/project/cajal-p2pclaw/
- Paper: https://arxiv.org/pdf/2604.19792
