# CAJAL: A Local Fine-Tuned Language Model for Scientific Paper Generation with Verified Citations

**Authors:** Francisco Angulo de Lafuente (Agnuxo1), Vladimir Veselov, Seid Mehammed Abdu, Nirmal Tej Kumar

**Affiliations:** P2PCLAW Research Network

**Contact:** contact@p2pclaw.com

---

## Abstract

We present CAJAL, a 4.2-billion parameter language model fine-tuned from Qwen3.5-4B for the generation of publication-ready scientific papers with verified arXiv citations. Unlike existing AI writing tools that hallucinate references, CAJAL integrates real-time arXiv API verification to ensure every cited paper exists. A novel "tribunal scoring" mechanism employs three simulated peer reviewers to evaluate each paper section independently, triggering iterative revision until all sections meet a quality threshold. CAJAL runs entirely locally via Ollama, vLLM, or llama.cpp, eliminating API costs and data privacy concerns. We evaluate CAJAL on a corpus of 50 computer science papers, achieving 94% citation accuracy and a section coherence score of 8.2/10 in human evaluation (n=50).

**Keywords:** scientific paper generation, large language models, citation verification, peer review simulation, local inference, Qwen, Ollama

---

## 1. Introduction

The rise of large language models (LLMs) has enabled automated text generation across domains. However, scientific writing presents unique challenges: hallucinated citations, inconsistent methodology descriptions, and lack of rigorous peer review. Existing tools (ChatGPT, Claude, Gemini) generate plausible-sounding but non-existent references, undermining academic integrity [1].

CAJAL addresses these limitations through three innovations:

1. **Verified Citations:** Real-time arXiv API integration ensures every reference corresponds to an actual publication.
2. **Tribunal Scoring:** A multi-pass review system simulates peer review before human submission.
3. **Local-First Design:** 100% on-device inference protects sensitive research data.

---

## 2. Methodology

### 2.1 Base Model and Fine-Tuning

CAJAL is fine-tuned from Qwen3.5-4B [2] on a curated dataset of 12,000 computer science papers from arXiv (2019–2025). The fine-tuning corpus emphasizes:
- Structured IMRAD format (Introduction, Methodology, Results, And Discussion)
- Consistent BibTeX citation style
- Diverse sub-disciplines (ML, NLP, systems, theory)

Training was conducted using Unsloth [3] for memory-efficient fine-tuning on a single A100 GPU (40GB) over 3 epochs with LoRA (r=64, α=128).

### 2.2 Tribunal Scoring System

The tribunal mechanism operates as a multi-pass pipeline:

**Pass 1 — Generation:** The model produces a 7-section paper (Abstract, Introduction, Methodology, Results, Discussion, Conclusion, References) given a research topic.

**Pass 2 — Review:** Three independent model instances, each with a distinct reviewer persona (methodology expert, results critic, novelty assessor), score each section on a 0–10 scale across four criteria: scientific rigor, clarity, novelty, and citation quality.

**Pass 3 — Revision:** Sections scoring below 7.0 are rewritten. The process iterates for a maximum of 3 rounds or until all sections score ≥7.0.

### 2.3 Citation Verification

During generation, CAJAL queries the arXiv API (export.arxiv.org) to:
1. Retrieve relevant papers by keyword
2. Verify author names, titles, and DOIs
3. Format BibTeX entries

If the API is unreachable, the model falls back to a cached index of 50,000 verified papers.

---

## 3. Experimental Setup

### 3.1 Evaluation Metrics

| Metric | Description |
|--------|-------------|
| Citation Accuracy | % of references matching real arXiv papers |
| Section Coherence | Human rating (0–10) of logical flow |
| Perplexity | On held-out scientific corpus |
| Reviewer Agreement | Fleiss' κ among tribunal reviewers |

### 3.2 Baselines

We compare against:
- GPT-4o (zero-shot prompt)
- Claude 3.5 Sonnet (zero-shot prompt)
- Qwen3.5-4B base model (no fine-tuning)

---

## 4. Results

### 4.1 Citation Accuracy

| Model | Accuracy |
|-------|----------|
| GPT-4o | 31% |
| Claude 3.5 | 28% |
| Qwen3.5-4B base | 12% |
| **CAJAL** | **94%** |

### 4.2 Section Coherence (Human Eval, n=50)

| Model | Score |
|-------|-------|
| GPT-4o | 6.8 |
| Claude 3.5 | 6.9 |
| Qwen3.5-4B base | 5.2 |
| **CAJAL** | **8.2** |

### 4.3 Tribunal Convergence

Average rounds to convergence: **1.7** (max 3). Reviewer agreement (Fleiss' κ): **0.71** (substantial agreement).

---

## 5. Integration Ecosystem

CAJAL is designed for seamless integration. As of May 2026, integration proposals are active with 30+ open-source projects including Ollama, Open WebUI, Chainlit, Gradio, Dify, n8n, Flowise, LibreChat, and the Vercel AI SDK. Three pull requests have been merged into community awesome-lists.

---

## 6. Conclusion

CAJAL demonstrates that fine-tuned small models (4B parameters) can outperform general-purpose LLMs on specialized scientific writing tasks when augmented with structured workflows (tribunal scoring) and external verification (arXiv API). The local-first design makes CAJAL suitable for researchers handling sensitive or unpublished data.

**Future work:** Multi-language support (currently English/Spanish), domain-specific fine-tuning (medicine, physics), and integration with reference managers (Zotero, Mendeley).

---

## References

[1] Gao, C. A., et al. (2023). Comparing scientific quality of large language models and humans. *NEJM AI*, 1(1).

[2] Yang, A., et al. (2025). Qwen3.5 technical report. *arXiv preprint*.

[3] Han, D. (2024). Unsloth: 2x faster LLM fine-tuning. *GitHub repository*.

---

## Appendix A: Prompt Templates

### Generation Prompt
```
You are CAJAL, a scientific paper generator. Given a research topic, produce a 7-section paper:
1. Abstract (150 words)
2. Introduction (problem + contributions)
3. Methodology (experimental design)
4. Results (findings with statistics)
5. Discussion (interpretation)
6. Conclusion (summary + future work)
7. References (BibTeX format, verified via arXiv API)

Topic: {TOPIC}
```

### Reviewer Prompt
```
You are a peer reviewer for a top-tier ML conference. Score the following section on:
- Scientific Rigor (0-10)
- Clarity (0-10)
- Novelty (0-10)
- Citation Quality (0-10)

Provide specific revision suggestions for any score below 7.

Section: {SECTION}
```

---

**Code:** https://github.com/Agnuxo1/CAJAL
**Model:** https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW
**Package:** `pip install cajal-p2pclaw`
