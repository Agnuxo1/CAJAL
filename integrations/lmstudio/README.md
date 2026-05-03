# CAJAL for LM Studio

## Setup

1. Download CAJAL model from [HuggingFace](https://huggingface.co/Agnuxo)
2. Open LM Studio
3. Go to **Developer** → **My Models**
4. Click **Load from file** → Select `cajal-p2pclaw.Q4_K_M.gguf`

## Configuration

```json
{
  "name": "CAJAL Paper Generator",
  "description": "Scientific paper generation with peer review",
  "systemPrompt": "You are CAJAL...",
  "temperature": 0.7,
  "topP": 0.9,
  "maxTokens": 4096
}
```

## Usage

**Prompt template:**
```
Generate a scientific paper on: [your topic]

Requirements:
- 7 sections (Abstract through Conclusion)
- Real arXiv citations
- Academic tone
- After drafting, score each section 0-10
- Rewrite sections scoring <7
```

## Links

- Repo: https://github.com/Agnuxo1/CAJAL
- Paper: https://arxiv.org/pdf/2604.19792
- PyPI: https://pypi.org/project/cajal-p2pclaw/

---

**Need help?** Open an issue: https://github.com/Agnuxo1/CAJAL/issues
