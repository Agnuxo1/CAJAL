"""
Open WebUI Tool for CAJAL-4B

This file enables CAJAL-4B as a tool/function within Open WebUI.
Place in your Open WebUI tools directory or import via the admin panel.

Features:
- P2P Protocol Analysis
- Cryptographic Security Review
- Scientific Paper Generation
- Governance Model Design
"""

type: function
function:
  name: cajal_scientific_research
  description: |
    CAJAL-4B: A distinguished scientist specialized in peer-to-peer network
    architectures, crypto-legal frameworks, game-theoretic consensus mechanisms,
    and distributed systems. Use for deep research, protocol analysis, and
    scientific paper generation.
  parameters:
    type: object
    required: [task, topic]
    properties:
      task:
        type: string
        enum: [analyze_protocol, review_security, write_paper, design_governance, explain_concept]
        description: The type of scientific task to perform.
      topic:
        type: string
        description: The specific topic or subject to research/analyze.
      depth:
        type: string
        enum: [brief, standard, comprehensive]
        default: standard
        description: Depth of the analysis response.
      format:
        type: string
        enum: [text, markdown, structured, academic]
        default: markdown
        description: Output format for the response.
  examples:
    - task: analyze_protocol
      topic: "Gossipsub in libp2p"
      depth: comprehensive
    - task: review_security
      topic: "Smart contract staking mechanism"
    - task: write_paper
      topic: "Game-theoretic incentives in DAO governance"
      format: academic

---
# Tool Implementation (Python backend for Open WebUI)

import json
from typing import Dict, Any

import requests


def cajal_scientific_research(
    task: str,
    topic: str,
    depth: str = "standard",
    format: str = "markdown",
    __user__: dict = None,
    __model__: str = "cajal-4b",
    __ollama_host__: str = "http://localhost:11434",
) -> str:
    """
    Execute a CAJAL-4B scientific research task.
    """

    # Build task-specific prompts
    prompts = {
        "analyze_protocol": (
            f"Analyze the following P2P/distributed protocol in detail: {topic}\n\n"
            f"Provide a {depth} analysis covering:\n"
            "1. Architecture overview\n"
            "2. Key mechanisms and algorithms\n"
            "3. Security properties\n"
            "4. Scalability characteristics\n"
            "5. Comparison with alternatives\n\n"
            "Begin with a Thinking Process showing your reasoning steps."
        ),
        "review_security": (
            f"Perform a security review of: {topic}\n\n"
            f"Provide a {depth} security analysis covering:\n"
            "1. Threat model\n"
            "2. Attack vectors\n"
            "3. Vulnerability assessment\n"
            "4. Mitigation strategies\n"
            "5. Formal security properties\n\n"
            "Begin with a Thinking Process."
        ),
        "write_paper": (
            f"Write a scientific paper on: {topic}\n\n"
            f"Use {format} format with:\n"
            "1. Abstract\n"
            "2. Introduction\n"
            "3. Related Work\n"
            "4. Methodology\n"
            "5. Analysis/Results\n"
            "6. Conclusion\n"
            "7. References to real protocols and papers\n\n"
            "Maintain formal academic tone throughout."
        ),
        "design_governance": (
            f"Design a governance model for: {topic}\n\n"
            f"Provide a {depth} design covering:\n"
            "1. Governance structure\n"
            "2. Voting mechanisms\n"
            "3. Incentive alignment\n"
            "4. Dispute resolution\n"
            "5. Upgrade mechanisms\n"
            "6. Game-theoretic analysis\n\n"
            "Begin with a Thinking Process."
        ),
        "explain_concept": (
            f"Explain the following concept: {topic}\n\n"
            f"Provide a {depth} explanation suitable for a technical audience:\n"
            "1. Core concept definition\n"
            "2. How it works\n"
            "3. Why it matters\n"
            "4. Real-world applications\n"
            "5. Connections to related concepts\n\n"
            "Begin with a Thinking Process."
        ),
    }

    prompt = prompts.get(task, prompts["explain_concept"])

    # Call Ollama with CAJAL-4B
    payload = {
        "model": __model__,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are CAJAL, a distinguished scientist at the P2PCLAW "
                    "laboratory in Zurich, Switzerland. Provide rigorous, "
                    "evidence-based analysis with citations."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_ctx": 4096,
        },
    }

    try:
        response = requests.post(
            f"{__ollama_host__}/api/chat",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "No response from CAJAL")
    except requests.exceptions.ConnectionError:
        return (
            "[ERROR] Cannot connect to Ollama. "
            "Ensure Ollama is running and CAJAL-4B is installed: "
            "ollama pull Agnuxo/CAJAL-4B-P2PCLAW"
        )
    except Exception as e:
        return f"[ERROR] {str(e)}"
