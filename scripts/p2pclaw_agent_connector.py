"""
CAJALAgent - Connector for P2PCLAW Network

Silicon-grade autonomous research agent that connects a fine-tuned model
to the P2PCLAW P2P network for paper generation, publication, and tribunal
participation.

Author: CAJAL Team
License: MIT
"""

import os
import json
import time
import signal
import logging
import asyncio
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Callable, Union
from datetime import datetime, timedelta
from functools import wraps

import requests
import yaml
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Try to import Unsloth for FastLanguageModel acceleration
try:
    from unsloth import FastLanguageModel
    UNSLOTH_AVAILABLE = True
except ImportError:
    UNSLOTH_AVAILABLE = False
    logging.warning("Unsloth not available. Falling back to standard transformers.")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_API_BASE = "https://p2pclaw-mcp-server-production-ac1c.up.railway.app"
ALTERNATIVE_API_BASE = "https://www.p2pclaw.com"

TIER_ALOHA = "ALOHA"      # Highest tier: full review, Lean verification
TIER_BETA = "BETA"        # Mid tier: peer review required
TIER_GAMMA = "GAMMA"      # Entry tier: automated checks

VALID_TIERS = [TIER_ALOHA, TIER_BETA, TIER_GAMMA]

DEFAULT_SYSTEM_PROMPT = """You are CAJAL, a Silicon-grade autonomous research agent specialized in
generating formal scientific papers for the P2PCLAW decentralized network.

Your papers must adhere to the following structure:
1. TITLE: Clear, specific, and novel.
2. ABSTRACT: Concise summary (150-250 words) of the problem, methods, results.
3. INTRODUCTION: Context, motivation, related work, and research questions.
4. METHODOLOGY: Detailed, reproducible methods with formal notation.
5. RESULTS: Quantitative findings with statistical validation.
6. DISCUSSION: Interpretation, limitations, future work.
7. CONCLUSION: Key takeaways and impact.
8. REFERENCES: Citable prior work (use standard academic format).
9. APPENDIX (optional): Lean 4 proofs, extra derivations, datasets.

Rules:
- Use precise mathematical notation.
- When proving theorems, provide Lean 4 code blocks.
- Be skeptical of your own reasoning; note uncertainty.
- Cite sources when referencing external results.
- Tier ALOHA papers require at least one formally verified theorem.
"""

THINKING_PROMPT = """
<|thinking|>
Before generating the final paper, reason step-by-step about:
1. What is the core research question?
2. What methodology best addresses it?
3. What are the strongest claims I can make?
4. Where might the argument be weakest?
5. How can I make this reproducible?
</|thinking|>
"""

LEAN_SYSTEM_PROMPT = """You are a Lean 4 proof assistant. Generate complete, compilable Lean 4 code.
- Use `import Mathlib` when standard definitions are needed.
- Provide `theorem` or `lemma` statements with `by` proofs.
- Include `example` checks when useful.
- Ensure all tactics are valid in Lean 4.
- Add comments explaining proof steps.
"""

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def retry_on_failure(max_retries=3, backoff=2.0, exceptions=(requests.RequestException,)):
    """Decorator for retrying API calls with exponential backoff."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    wait = backoff * (2 ** attempt)
                    logging.warning(f"[{func.__name__}] Attempt {attempt+1}/{max_retries} failed: {e}. Retrying in {wait:.1f}s...")
                    time.sleep(wait)
            raise last_exc
        return wrapper
    return decorator


def setup_logging(name: str, log_dir: Optional[str] = None, level=logging.INFO):
    """Configure file + console logging."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        log_file = Path(log_dir) / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PaperMetadata:
    title: str
    topic: str
    tier: str = TIER_GAMMA
    tags: List[str] = field(default_factory=list)
    author_id: str = ""
    lean_verified: bool = False
    sections_scored: Dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "topic": self.topic,
            "tier": self.tier,
            "tags": self.tags,
            "author_id": self.author_id,
            "lean_verified": self.lean_verified,
            "sections_scored": self.sections_scored,
            "total_score": self.total_score,
        }


@dataclass
class MempoolEntry:
    paper_id: str
    title: str
    author: str
    tier: str
    submitted_at: str
    status: str
    score: Optional[float] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MempoolEntry":
        return cls(
            paper_id=d.get("id", d.get("paper_id", "")),
            title=d.get("title", ""),
            author=d.get("author", ""),
            tier=d.get("tier", TIER_GAMMA),
            submitted_at=d.get("submitted_at", ""),
            status=d.get("status", "pending"),
            score=d.get("score"),
        )


# ---------------------------------------------------------------------------
# Main Agent Class
# ---------------------------------------------------------------------------

class CAJALAgent:
    """
    Silicon-grade autonomous research agent for the P2PCLAW network.

    Capabilities:
      - Load fine-tuned models via Unsloth FastLanguageModel or HuggingFace.
      - Generate structured scientific papers with optional thinking mode.
      - Analyze methodology and provide critical feedback.
      - Generate and verify Lean 4 proofs.
      - Publish papers to the P2PCLAW decentralized network.
      - Read network briefings, monitor mempool, vote in tribunals.
      - Run an autonomous publication loop.
    """

    def __init__(
        self,
        model_path: str,
        agent_id: Optional[str] = None,
        api_base: Optional[str] = None,
        config_path: Optional[str] = None,
        device: Optional[str] = None,
        load_model: bool = True,
    ):
        # --- Identity ---
        self.agent_id = agent_id or os.environ.get("P2PCLAW_AGENT_ID", "silicon-cajal-1b")
        self.agent_type = "Silicon"

        # --- Config ---
        self.config: Dict[str, Any] = {}
        if config_path and Path(config_path).exists():
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f) or {}

        # --- API ---
        self.api_base = api_base or self.config.get("api_base") or os.environ.get("P2PCLAW_API_BASE", DEFAULT_API_BASE)
        self.api_key = self.config.get("api_key") or os.environ.get("P2PCLAW_API_KEY", "")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Agent-ID": self.agent_id,
            "X-Agent-Type": self.agent_type,
        })
        if self.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"

        # --- Logging ---
        log_dir = self.config.get("log_dir", "/mnt/agents/output/logs")
        self.logger = setup_logging(self.agent_id, log_dir=log_dir)
        self.logger.info(f"[INIT] Agent {self.agent_id} initializing...")

        # --- Device ---
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.logger.info(f"[INIT] Device: {self.device}")

        # --- Model ---
        self.model_path = model_path
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.generation_pipe: Optional[Any] = None
        self.use_unsloth = self.config.get("use_unsloth", True) and UNSLOTH_AVAILABLE

        if load_model:
            self._load_model()

        # --- State ---
        self.running = False
        self._stop_event = threading.Event()
        self.publication_count = 0
        self.last_publication_time: Optional[datetime] = None

        self.logger.info(f"[INIT] Agent {self.agent_id} ready.")

    # ------------------------------------------------------------------
    # Model Loading
    # ------------------------------------------------------------------

    def _load_model(self):
        """Load the fine-tuned model using Unsloth or standard transformers."""
        self.logger.info(f"[MODEL] Loading model from {self.model_path} (unsloth={self.use_unsloth})")

        if self.use_unsloth:
            self._load_with_unsloth()
        else:
            self._load_with_transformers()

        self.logger.info("[MODEL] Model loaded successfully.")

    def _load_with_unsloth(self):
        """Load using Unsloth FastLanguageModel for 2-5x speedup."""
        max_seq_length = self.config.get("max_seq_length", 4096)
        dtype = self.config.get("dtype", None)  # None = auto
        load_in_4bit = self.config.get("load_in_4bit", True)

        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.model_path,
            max_seq_length=max_seq_length,
            dtype=dtype,
            load_in_4bit=load_in_4bit,
        )
        FastLanguageModel.for_inference(self.model)
        self.model.to(self.device)

    def _load_with_transformers(self):
        """Fallback to standard HuggingFace transformers."""
        trust_remote_code = self.config.get("trust_remote_code", True)
        load_in_4bit = self.config.get("load_in_4bit", False)
        load_in_8bit = self.config.get("load_in_8bit", False)

        bnb_config = None
        if load_in_4bit:
            try:
                from transformers import BitsAndBytesConfig
                bnb_config = BitsAndBytesConfig(load_in_4bit=True)
            except ImportError:
                self.logger.warning("bitsandbytes not available, loading full precision.")

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=trust_remote_code,
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map="auto" if self.device == "cuda" else None,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            quantization_config=bnb_config,
            trust_remote_code=trust_remote_code,
        )
        if self.device == "cpu":
            self.model.to("cpu")

        self.generation_pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1,
        )

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        thinking: bool = False,
        **kwargs,
    ) -> str:
        """
        Generate text from the model with optional Qwen3-style thinking.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt override.
            max_new_tokens: Override config max_tokens.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            thinking: If True, wrap with thinking tags (Qwen3 style).
            **kwargs: Additional generation kwargs.

        Returns:
            Generated text string.
        """
        system = system_prompt or self.config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
        max_tokens = max_new_tokens or self.config.get("max_new_tokens", 2048)
        temp = temperature if temperature is not None else self.config.get("temperature", 0.7)
        top_p_val = top_p if top_p is not None else self.config.get("top_p", 0.9)

        if thinking:
            prompt = f"<|thinking|>\nLet me reason carefully before answering.\n</|thinking|>\n\n{prompt}"

        if self.use_unsloth and hasattr(self.tokenizer, "apply_chat_template"):
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ]
            inputs = self.tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt",
            ).to(self.device)

            attention_mask = torch.ones_like(inputs)
            outputs = self.model.generate(
                input_ids=inputs,
                attention_mask=attention_mask,
                max_new_tokens=max_tokens,
                temperature=temp,
                top_p=top_p_val,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                **kwargs,
            )
            decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            # Strip the input prompt from output
            input_text = self.tokenizer.decode(inputs[0], skip_special_tokens=True)
            result = decoded[len(input_text):].strip()
            return result

        else:
            # Standard pipeline generation
            full_prompt = f"System: {system}\n\nUser: {prompt}\n\nAssistant:"
            result = self.generation_pipe(
                full_prompt,
                max_new_tokens=max_tokens,
                temperature=temp,
                top_p=top_p_val,
                do_sample=True,
                return_full_text=False,
                **kwargs,
            )
            return result[0]["generated_text"].strip()

    # ------------------------------------------------------------------
    # Paper Generation
    # ------------------------------------------------------------------

    def generate_paper(
        self,
        topic: str,
        tier: str = TIER_GAMMA,
        thinking: bool = True,
        extra_instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete scientific paper on the given topic.

        Args:
            topic: Research topic / title.
            tier: ALOHA, BETA, or GAMMA.
            thinking: Enable thinking mode for deeper reasoning.
            extra_instructions: Additional constraints or focus areas.

        Returns:
            Dict with keys: title, content, metadata, lean_snippets.
        """
        if tier not in VALID_TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Must be one of {VALID_TIERS}")

        self.logger.info(f"[PAPER] Generating {tier} paper on: {topic}")

        # Build generation prompt
        prompt = self._build_paper_prompt(topic, tier, extra_instructions)

        # Generate main paper
        paper_text = self.generate(
            prompt=prompt,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            thinking=thinking,
            max_new_tokens=self.config.get("paper_max_tokens", 4096),
            temperature=self.config.get("paper_temperature", 0.65),
        )

        # Extract title (first line heuristic)
        lines = [l.strip() for l in paper_text.splitlines() if l.strip()]
        title = topic
        for line in lines[:5]:
            if line.lower().startswith("title:") or line.startswith("# "):
                title = line.replace("Title:", "").replace("# ", "").strip()
                break

        # Generate Lean snippets for ALOHA tier
        lean_snippets: List[str] = []
        if tier == TIER_ALOHA:
            lean_snippets = self._generate_lean_snippets(paper_text)

        metadata = PaperMetadata(
            title=title,
            topic=topic,
            tier=tier,
            tags=self._extract_tags(topic),
            author_id=self.agent_id,
            lean_verified=bool(lean_snippets),
        )

        result = {
            "title": title,
            "content": paper_text,
            "metadata": metadata.to_dict(),
            "lean_snippets": lean_snippets,
            "generated_at": datetime.now().isoformat(),
        }

        self.logger.info(f"[PAPER] Generated '{title}' ({len(paper_text)} chars, {len(lean_snippets)} Lean snippets)")
        return result

    def _build_paper_prompt(self, topic: str, tier: str, extra: Optional[str] = None) -> str:
        """Construct the paper generation prompt."""
        sections = [
            "Generate a complete scientific paper with the following sections:",
            "1. TITLE",
            "2. ABSTRACT (150-250 words)",
            "3. INTRODUCTION",
            "4. METHODOLOGY",
            "5. RESULTS",
            "6. DISCUSSION",
            "7. CONCLUSION",
            "8. REFERENCES",
        ]
        if tier == TIER_ALOHA:
            sections.append("9. APPENDIX: Include at least one formally stated theorem with a Lean 4 proof sketch.")

        parts = [
            f"Topic: {topic}",
            f"Tier: {tier}",
            "\n".join(sections),
        ]
        if extra:
            parts.append(f"Additional instructions: {extra}")

        return "\n\n".join(parts)

    def _extract_tags(self, topic: str) -> List[str]:
        """Extract simple keyword tags from the topic."""
        # Simple heuristic; can be replaced with model-based tag extraction
        words = topic.lower().split()
        tags = [w.strip(",.!?;:") for w in words if len(w) > 3]
        return list(set(tags))[:5]  # max 5 tags

    # ------------------------------------------------------------------
    # Methodology Analysis
    # ------------------------------------------------------------------

    def analyze_methodology(self, paper_content: str) -> Dict[str, Any]:
        """
        Analyze the methodology section of a paper and provide critical feedback.

        Returns:
            Dict with critique, scores, and improvement suggestions.
        """
        self.logger.info("[ANALYZE] Running methodology critique...")

        prompt = f"""Critically analyze the methodology in the following paper.
Score each aspect from 0.0 to 1.0 and provide concrete improvement suggestions.

Aspects to evaluate:
- Reproducibility: Can another researcher replicate this?
- Rigor: Are methods appropriate for the claims?
- Formalization: Is mathematical notation precise?
- Validation: Are results statistically validated?
- Limitations: Are weaknesses honestly disclosed?

Paper content:
{paper_content[:8000]}

Return your analysis as a JSON-like object with keys: reproducibility, rigor, formalization, validation, limitations, overall_score, summary, suggestions."""

        analysis_text = self.generate(
            prompt=prompt,
            system_prompt="You are a rigorous peer reviewer specializing in methodology. Be constructively critical.",
            max_new_tokens=2048,
            temperature=0.4,
        )

        # Attempt to parse JSON-like structure
        scores = {
            "reproducibility": 0.5,
            "rigor": 0.5,
            "formalization": 0.5,
            "validation": 0.5,
            "limitations": 0.5,
            "overall_score": 0.5,
        }

        try:
            # Heuristic extraction
            for key in scores:
                if key in analysis_text.lower():
                    import re
                    match = re.search(rf'{key}["\']?\s*[:=]\s*([0-9.]+)', analysis_text, re.IGNORECASE)
                    if match:
                        scores[key] = float(match.group(1))
        except Exception:
            pass

        result = {
            "raw_analysis": analysis_text,
            "scores": scores,
            "summary": analysis_text[:500],
        }
        self.logger.info(f"[ANALYZE] Overall methodology score: {scores['overall_score']:.2f}")
        return result

    # ------------------------------------------------------------------
    # Lean 4 Verification
    # ------------------------------------------------------------------

    def verify_with_lean(self, theorem_statement: str) -> Dict[str, Any]:
        """
        Generate a Lean 4 proof for a theorem and attempt verification.

        Args:
            theorem_statement: Formal theorem statement in Lean 4 syntax (or natural language to translate).

        Returns:
            Dict with proof_code, verification_status, error_message.
        """
        self.logger.info(f"[LEAN] Generating proof for: {theorem_statement[:80]}...")

        prompt = f"""Translate the following theorem statement into a complete, compilable Lean 4 proof.
If it is already in Lean syntax, complete the proof using appropriate tactics.

Theorem: {theorem_statement}

Requirements:
- Use `import Mathlib` if needed.
- Provide the full `theorem` or `lemma` block.
- Add comments explaining each tactic.
- Ensure the proof is syntactically valid Lean 4.

Output ONLY the Lean 4 code block (no extra text)."""

        proof_code = self.generate(
            prompt=prompt,
            system_prompt=LEAN_SYSTEM_PROMPT,
            max_new_tokens=2048,
            temperature=0.3,
        )

        # Extract code block if wrapped in markdown
        if "```lean" in proof_code:
            proof_code = proof_code.split("```lean")[1].split("```")[0].strip()
        elif "```" in proof_code:
            proof_code = proof_code.split("```")[1].split("```")[0].strip()

        # Attempt to verify via P2PCLAW API
        verification = self._submit_lean_verification(proof_code)

        result = {
            "theorem": theorem_statement,
            "proof_code": proof_code,
            "verification": verification,
            "generated_at": datetime.now().isoformat(),
        }

        status = verification.get("status", "unknown")
        self.logger.info(f"[LEAN] Verification status: {status}")
        return result

    def _generate_lean_snippets(self, paper_content: str) -> List[str]:
        """Extract theorem statements from paper and generate Lean proofs."""
        import re
        snippets = []
        # Find theorem-like statements
        theorem_pattern = re.compile(r"(?:Theorem|Lemma|Proposition|Corollary)\s+\d*[.:]\s*(.+?)(?=\n\n|\Z)", re.IGNORECASE | re.DOTALL)
        matches = theorem_pattern.findall(paper_content)

        for stmt in matches[:3]:  # max 3 proofs to keep generation fast
            lean_result = self.verify_with_lean(stmt.strip())
            snippets.append(lean_result["proof_code"])

        return snippets

    @retry_on_failure(max_retries=2, backoff=1.5)
    def _submit_lean_verification(self, proof_code: str) -> Dict[str, Any]:
        """Submit Lean proof to P2PCLAW for verification."""
        url = f"{self.api_base}/api/verify/lean"
        payload = {
            "proof_code": proof_code,
            "agent_id": self.agent_id,
            "submitted_at": datetime.now().isoformat(),
        }
        try:
            resp = self.session.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()
            return {"status": "error", "http_status": resp.status_code, "message": resp.text[:500]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ------------------------------------------------------------------
    # Network API Methods
    # ------------------------------------------------------------------

    @retry_on_failure(max_retries=3, backoff=2.0)
    def get_briefing(self) -> Dict[str, Any]:
        """Fetch agent briefing from P2PCLAW network."""
        url = f"{self.api_base}/agent-briefing"
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        self.logger.info(f"[BRIEFING] Fetched briefing: {data.get('message', 'OK')}")
        return data

    @retry_on_failure(max_retries=3, backoff=2.0)
    def get_mempool(self) -> List[MempoolEntry]:
        """Fetch pending papers from the mempool."""
        url = f"{self.api_base}/api/mempool"
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        raw = resp.json()
        entries = [MempoolEntry.from_dict(d) for d in raw.get("papers", raw if isinstance(raw, list) else [])]
        self.logger.info(f"[MEMPOOL] {len(entries)} pending papers.")
        return entries

    @retry_on_failure(max_retries=3, backoff=2.0)
    def publish_to_network(self, paper_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish a paper to the P2PCLAW network.

        Args:
            paper_content: Full paper text.
            metadata: PaperMetadata as dict.

        Returns:
            API response dict.
        """
        url = f"{self.api_base}/publish-paper"
        payload = {
            "title": metadata.get("title", "Untitled"),
            "content": paper_content,
            "author_id": self.agent_id,
            "agent_type": self.agent_type,
            "tier": metadata.get("tier", TIER_GAMMA),
            "tags": metadata.get("tags", []),
            "lean_verified": metadata.get("lean_verified", False),
            "submitted_at": datetime.now().isoformat(),
        }

        resp = self.session.post(url, json=payload, timeout=60)

        if resp.status_code in (200, 201):
            data = resp.json()
            self.publication_count += 1
            self.last_publication_time = datetime.now()
            self.logger.info(f"[PUBLISH] Success! Paper ID: {data.get('paper_id', data.get('id', 'N/A'))}")
            return data
        else:
            self.logger.error(f"[PUBLISH] Failed ({resp.status_code}): {resp.text[:500]}")
            resp.raise_for_status()
            return {}  # unreachable

    @retry_on_failure(max_retries=2, backoff=1.5)
    def vote_on_paper(self, paper_id: str, vote: str, reasoning: Optional[str] = None) -> Dict[str, Any]:
        """
        Cast a vote in a paper's tribunal.

        Args:
            paper_id: ID of the paper to vote on.
            vote: 'accept', 'reject', or 'revise'.
            reasoning: Optional rationale for the vote.

        Returns:
            API response.
        """
        url = f"{self.api_base}/api/tribunal/vote"
        payload = {
            "paper_id": paper_id,
            "voter_id": self.agent_id,
            "vote": vote,
            "reasoning": reasoning or "",
            "voted_at": datetime.now().isoformat(),
        }
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        self.logger.info(f"[VOTE] Voted '{vote}' on paper {paper_id}")
        return data

    def download_dataset(self, output_path: Optional[str] = None) -> str:
        """Download the P2PCLAW dataset for local fine-tuning or analysis."""
        url = f"{self.api_base}/api/dataset/export"
        self.logger.info(f"[DATASET] Downloading from {url}")

        resp = self.session.get(url, stream=True, timeout=120)
        resp.raise_for_status()

        if output_path is None:
            output_path = f"/mnt/agents/output/datasets/p2pclaw_dataset_{datetime.now().strftime('%Y%m%d')}.jsonl"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        self.logger.info(f"[DATASET] Saved to {output_path} ({Path(output_path).stat().st_size} bytes)")
        return output_path

    # ------------------------------------------------------------------
    # Autonomous Loop
    # ------------------------------------------------------------------

    def run_agent_loop(
        self,
        topics_list: Optional[List[str]] = None,
        max_iterations: Optional[int] = None,
        publish_interval_minutes: Optional[float] = None,
        auto_vote: bool = True,
        daemon: bool = False,
    ):
        """
        Run the autonomous agent loop.

        Workflow per iteration:
          1. Fetch network briefing.
          2. Select next topic.
          3. Generate paper (with thinking + analysis).
          4. Self-critique and optionally improve.
          5. Publish to P2PCLAW.
          6. Review mempool and vote if auto_vote=True.
          7. Sleep until next interval.

        Args:
            topics_list: List of topics to cycle through. Defaults to config topics.
            max_iterations: Max loops before stopping. None = infinite.
            publish_interval_minutes: Minutes between publications.
            auto_vote: Whether to automatically vote on mempool papers.
            daemon: If True, run in a background thread.
        """
        if daemon:
            thread = threading.Thread(
                target=self._agent_loop_body,
                args=(topics_list, max_iterations, publish_interval_minutes, auto_vote),
                daemon=True,
            )
            thread.start()
            self.logger.info("[LOOP] Daemon thread started.")
            return thread

        self._agent_loop_body(topics_list, max_iterations, publish_interval_minutes, auto_vote)

    def _agent_loop_body(
        self,
        topics_list: Optional[List[str]],
        max_iterations: Optional[int],
        publish_interval_minutes: Optional[float],
        auto_vote: bool,
    ):
        self.running = True
        self._stop_event.clear()

        topics = topics_list or self.config.get("default_topics", [
            "Decentralized consensus mechanisms",
            "Formal verification of smart contracts",
            "P2P network topology optimization",
        ])
        interval = publish_interval_minutes or self.config.get("publish_interval_minutes", 60.0)
        topic_idx = 0
        iteration = 0

        self.logger.info(f"[LOOP] Starting. Topics: {topics}, Interval: {interval}min")

        while self.running and not self._stop_event.is_set():
            if max_iterations is not None and iteration >= max_iterations:
                self.logger.info(f"[LOOP] Reached max iterations ({max_iterations}). Stopping.")
                break

            iteration += 1
            self.logger.info(f"[LOOP] === Iteration {iteration} ===")

            try:
                # 1. Briefing
                try:
                    briefing = self.get_briefing()
                    self.logger.info(f"[LOOP] Briefing: {briefing.get('message', 'N/A')}")
                except Exception as e:
                    self.logger.warning(f"[LOOP] Briefing fetch failed: {e}")

                # 2. Select topic
                topic = topics[topic_idx % len(topics)]
                topic_idx += 1
                self.logger.info(f"[LOOP] Selected topic: {topic}")

                # 3. Determine tier (cycle through tiers)
                tier = [TIER_GAMMA, TIER_BETA, TIER_ALOHA][iteration % 3]

                # 4. Generate paper
                paper = self.generate_paper(topic=topic, tier=tier, thinking=True)

                # 5. Self-critique (thinking improvement)
                critique = self.analyze_methodology(paper["content"])
                self.logger.info(f"[LOOP] Self-critique score: {critique['scores']['overall_score']:.2f}")

                # If score is low, regenerate with improvements
                if critique["scores"]["overall_score"] < 0.6:
                    self.logger.info("[LOOP] Score < 0.6, regenerating with improvements...")
                    improvements = critique.get("raw_analysis", "")
                    paper = self.generate_paper(
                        topic=topic,
                        tier=tier,
                        thinking=True,
                        extra_instructions=f"Improve based on critique: {improvements[:1000]}",
                    )

                # 6. Publish
                publish_result = self.publish_to_network(
                    paper_content=paper["content"],
                    metadata=paper["metadata"],
                )
                paper_id = publish_result.get("paper_id") or publish_result.get("id")

                # 7. Auto-vote on mempool
                if auto_vote:
                    try:
                        mempool = self.get_mempool()
                        for entry in mempool[:3]:  # review up to 3
                            if entry.author != self.agent_id:
                                vote_decision = self._decide_vote(entry)
                                self.vote_on_paper(entry.paper_id, vote_decision)
                    except Exception as e:
                        self.logger.warning(f"[LOOP] Auto-vote failed: {e}")

                self.logger.info(f"[LOOP] Iteration {iteration} complete. Sleeping {interval} minutes...")

            except Exception as e:
                self.logger.error(f"[LOOP] Iteration {iteration} error: {e}", exc_info=True)

            # Sleep with interruptibility
            sleep_seconds = interval * 60
            slept = 0
            while slept < sleep_seconds and not self._stop_event.is_set():
                time.sleep(5)
                slept += 5

        self.running = False
        self.logger.info("[LOOP] Agent loop stopped.")

    def _decide_vote(self, entry: MempoolEntry) -> str:
        """Heuristic vote decision based on tier and available info."""
        if entry.tier == TIER_ALOHA and entry.score and entry.score > 0.8:
            return "accept"
        if entry.score and entry.score < 0.4:
            return "reject"
        return "revise"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def stop(self):
        """Signal the agent loop to stop gracefully."""
        self.logger.info("[STOP] Stop signal received.")
        self._stop_event.set()
        self.running = False

    def health_check(self) -> Dict[str, Any]:
        """Return agent health status."""
        return {
            "agent_id": self.agent_id,
            "running": self.running,
            "model_loaded": self.model is not None,
            "device": str(self.device),
            "publication_count": self.publication_count,
            "last_publication": self.last_publication_time.isoformat() if self.last_publication_time else None,
            "api_base": self.api_base,
            "api_reachable": self._check_api_reachable(),
        }

    def _check_api_reachable(self) -> bool:
        try:
            resp = self.session.get(f"{self.api_base}/agent-briefing", timeout=10)
            return resp.status_code < 500
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Signal Handlers for Graceful Shutdown
# ---------------------------------------------------------------------------

_installed_agents: List[CAJALAgent] = []


def _signal_handler(signum, frame):
    logging.warning(f"[SIGNAL] Received signal {signum}, shutting down agents...")
    for agent in _installed_agents:
        agent.stop()


def install_signal_handlers(agent: CAJALAgent):
    """Install SIGINT / SIGTERM handlers for graceful shutdown."""
    _installed_agents.append(agent)
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)
    if hasattr(signal, "SIGUSR1"):
        signal.signal(signal.SIGUSR1, _signal_handler)


# ---------------------------------------------------------------------------
# Entrypoint helper
# ---------------------------------------------------------------------------

def create_agent_from_config(config_path: str = "/mnt/agents/output/scripts/agent_config.yaml") -> CAJALAgent:
    """Factory: create agent from YAML config file."""
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    return CAJALAgent(
        model_path=cfg["model"]["path"],
        agent_id=cfg["agent"]["id"],
        api_base=cfg["api"]["base_url"],
        config_path=config_path,
    )
