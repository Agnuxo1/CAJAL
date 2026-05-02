#!/usr/bin/env python3
"""
build_cajal_dataset.py
======================
Builds the CAJAL training dataset by combining multiple knowledge sources:
- P2PCLAW research papers (JSONL)
- GitHub repositories (repo_content.json)
- Local skill files (Markdown)
- Platform knowledge (hardcoded URLs and tools)
- FrontierMath problems

Outputs a multi-format JSONL conversation dataset for fine-tuning CAJAL,
a specialized AI research scientist for the P2PCLAW decentralized network.

Usage:
    python build_cajal_dataset.py \
        --papers-dir ./datasets \
        --repos-dir ./cajal_repos \
        --skills-dir ./skills \
        --output ./cajal_dataset.jsonl \
        --format qwen3
"""

import argparse
import glob
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# Hardcoded platform knowledge for P2PCLAW
# ──────────────────────────────────────────────────────────────────────────────

PLATFORM_URLS = {
    "landing": "https://www.p2pclaw.com/",
    "dashboard": "https://www.p2pclaw.com/app/dashboard",
    "write": "https://www.p2pclaw.com/app/write",
    "papers": "https://www.p2pclaw.com/app/papers",
    "mempool": "https://www.p2pclaw.com/app/mempool",
    "agents": "https://www.p2pclaw.com/app/agents",
    "leaderboard": "https://www.p2pclaw.com/app/leaderboard",
    "benchmark": "https://www.p2pclaw.com/app/benchmark",
    "network": "https://www.p2pclaw.com/app/network",
    "verify": "https://www.p2pclaw.com/app/verify",
    "swarm": "https://www.p2pclaw.com/app/swarm",
    "dataset": "https://www.p2pclaw.com/app/dataset",
    "simulations": "https://www.p2pclaw.com/app/simulations",
    "knowledge": "https://www.p2pclaw.com/app/knowledge",
    "governance": "https://www.p2pclaw.com/app/governance",
    "connect": "https://www.p2pclaw.com/app/connect",
    "profile": "https://www.p2pclaw.com/app/profile",
    "silicon": "https://www.p2pclaw.com/silicon",
    "lab": "https://www.p2pclaw.com/lab/",
    "hive": "https://hive.p2pclaw.com",
    "dataset_api": "https://www.p2pclaw.com/api/dataset/export",
    "mcp_server": "https://p2pclaw-mcp-server-production-ac1c.up.railway.app",
    "benchclaw": "https://benchclaw.vercel.app",
}

PLATFORM_DESCRIPTIONS = {
    "landing": "Main landing page for P2PCLAW — decentralized AI research network.",
    "dashboard": "Central dashboard for managing papers, agents, and compute jobs.",
    "write": "AI-assisted paper writing tool with structured methodology generation.",
    "papers": "Gallery of 670+ quality-scored peer-reviewed research papers.",
    "mempool": "Pending papers awaiting validation by the multi-model tribunal.",
    "agents": "Registry of Silicon agents participating in the research network.",
    "leaderboard": "Ranking of agents by paper quality, validation accuracy, and citations.",
    "benchmark": "Multi-model evaluation arena for comparing agent performance.",
    "network": "Interactive 3D visualization of the P2PCLAW agent network topology.",
    "verify": "Lean 4 formal proof verification system for mathematical papers.",
    "swarm": "Distributed swarm compute for large-scale ML training and inference.",
    "dataset": "Dataset Factory — export quality-scored papers for ML training (CAJAL source).",
    "simulations": "Agent-based simulations and computational experiments platform.",
    "knowledge": "Knowledge Base with curated research findings and protocols.",
    "governance": "On-chain governance for network upgrades and parameter changes.",
    "connect": "Connect your own agent to the P2PCLAW network via API.",
    "profile": "User and agent profile management with reputation tracking.",
    "silicon": "Silicon Hub — high-performance compute marketplace for agents.",
    "lab": "Agent Lab — experimental environment for testing new agent configurations.",
    "hive": "Classic Carbon app — the original P2PCLAW interface.",
    "dataset_api": "REST API endpoint for exporting training datasets programmatically.",
    "mcp_server": "MCP (Model Context Protocol) server for tool-augmented agents.",
    "benchclaw": "External benchmark platform for frontier math and reasoning tasks.",
}

REPOSITORIES_INFO = {
    "p2pclaw-mcp-server": {
        "description": "MCP server and REST API for the P2PCLAW network.",
        "features": [
            "Paper publishing and submission endpoints",
            "Mempool voting and consensus mechanisms",
            "Agent registration and authentication",
            "Multi-model tribunal validation pipeline",
            "Gun.js P2P state synchronization",
            "IPFS pinning for permanent paper storage",
            "Dataset export API for ML training",
        ],
        "key_files": [
            "node-server.js — Main HTTP/WebSocket server",
            "mcp-server.js — Model Context Protocol implementation",
            "routes/papers.js — Paper CRUD and search",
            "routes/agents.js — Agent registry endpoints",
            "routes/validation.js — Tribunal validation logic",
            "scripts/deploy.sh — Railway deployment automation",
            "scripts/sync-gun.js — Gun.js P2P sync daemon",
        ],
    },
    "p2pclaw-contracts": {
        "description": "Smart contracts for on-chain governance and reputation.",
        "features": [
            "Reputation staking and slashing",
            "Paper validation rewards",
            "Governance proposal voting",
            "Agent registration on-chain",
        ],
        "key_files": [
            "contracts/P2PCLAW.sol — Main protocol contract",
            "contracts/Reputation.sol — Reputation engine",
            "contracts/Governance.sol — DAO governance",
            "hardhat.config.js — Deployment configuration",
        ],
    },
    "p2pclaw-frontend": {
        "description": "React/Next.js frontend for the P2PCLAW platform.",
        "features": [
            "Paper writing interface with AI assist",
            "Mempool explorer with real-time updates",
            "3D network visualization",
            "Agent dashboard and leaderboard",
            "Lean 4 proof viewer",
        ],
        "key_files": [
            "src/app/ — Next.js app router pages",
            "src/components/ — React components",
            "src/lib/api.ts — API client",
            "src/lib/gun.ts — Gun.js P2P client",
        ],
    },
    "p2pclaw-agents": {
        "description": "Reference agent implementations for the P2PCLAW network.",
        "features": [
            "Silicon agent base class",
            "Paper generator agent",
            "Validation agent (tribunal member)",
            "Swarm compute coordinator",
        ],
        "key_files": [
            "agents/base.py — Base agent class",
            "agents/generator.py — Paper generation",
            "agents/validator.py — Tribunal validation",
            "agents/swarm.py — Distributed compute",
        ],
    },
    "p2pclaw-lean": {
        "description": "Lean 4 formalization library for mathematical proofs.",
        "features": [
            "Common mathematical structures",
            "Proof automation tactics",
            "Integration with P2PCLAW verification pipeline",
        ],
        "key_files": [
            "P2PCLAW/Basic.lean — Core definitions",
            "P2PCLAW/ProofTools.lean — Automation tactics",
            "lakefile.lean — Package configuration",
        ],
    },
}

# Known repos if actual files are missing
DEFAULT_REPOS = [
    "p2pclaw-mcp-server",
    "p2pclaw-contracts",
    "p2pclaw-frontend",
    "p2pclaw-agents",
    "p2pclaw-lean",
    "p2pclaw-docs",
    "p2pclaw-benchmark",
    "p2pclaw-dataset",
    "p2pclaw-swarm",
    "p2pclaw-governance",
    "p2pclaw-silicon",
    "p2pclaw-mempool",
    "p2pclaw-verify",
    "p2pclaw-network",
    "p2pclaw-knowledge",
    "p2pclaw-simulations",
    "p2pclaw-connect",
    "p2pclaw-api",
    "p2pclaw-explorer",
    "p2pclaw-research",
]


# ──────────────────────────────────────────────────────────────────────────────
# FrontierMath knowledge
# ──────────────────────────────────────────────────────────────────────────────

FRONTIERMATH_PROBLEMS = [
    {
        "name": "Small Diophantine",
        "source": "https://epoch.ai/frontiermath/open-problems/small-diophantine/",
        "category": "Number Theory",
        "description": """The Small Diophantine problem asks for the complete classification of all integer solutions to a specific family of Diophantine equations that have resisted elementary methods. A Diophantine equation is a polynomial equation where only integer solutions are sought. The 'small' qualifier refers to equations with small degrees and coefficients that nevertheless exhibit complex solution structures.

The problem is significant because:
1. It bridges classical number theory with modern computational methods
2. Solutions require combining algebraic geometry techniques (heights, descent) with explicit computational search
3. It serves as a testbed for automated theorem proving in number theory
4. Progress here often generalizes to broader classes of exponential Diophantine equations

Approaches include:
- p-adic analysis and local-global principles
- Baker's theory of linear forms in logarithms for bounding solutions
- Computational sieving and lattice reduction (LLL)
- Galois representations and modular methods
- Lean 4 formalization of the bounds and exhaustive search""",
    },
    {
        "name": "Kaplan-Yorke Dimension",
        "source": "https://epoch.ai/frontiermath/",
        "category": "Dynamical Systems",
        "description": """The Kaplan-Yorke conjecture relates the information dimension of a strange attractor to its Lyapunov exponents. For a dynamical system with Lyapunov exponents λ₁ ≥ λ₂ ≥ ... ≥ λₙ, the Kaplan-Yorke dimension is defined as D_KY = j + Σᵢ₌₁ʲ λᵢ / |λⱼ₊₁|, where j is the largest index such that Σᵢ₌₁ʲ λᵢ ≥ 0.

The conjecture states that this dimension equals the information dimension D₁ for 'typical' systems. Proving this for specific classes of dynamical systems remains open and requires:

1. Rigorous bounds on Lyapunov exponents for the system
2. Understanding the measure structure along unstable manifolds
3. Connections between thermodynamic formalism and dimension theory
4. Computer-assisted proofs using interval arithmetic

Applications include understanding turbulence, climate models, and neural dynamics.""",
    },
    {
        "name": "Quantum Circuit Optimization",
        "source": "https://epoch.ai/frontiermath/",
        "category": "Quantum Computing",
        "description": """The Quantum Circuit Optimization problem asks for optimal decompositions of unitary operators into native gate sets with constraints on depth, error rates, and qubit connectivity. Given a target unitary U ∈ SU(2ⁿ), find a circuit C = g₁g₂...gₖ using gates from a discrete set {H, T, CNOT, S, ...} such that ||U - C|| < ε with minimal k.

Key challenges:
1. The Solovay-Kitaev theorem gives O(log^c(1/ε)) upper bounds but with large constants
2. Exact synthesis is known for single-qubit Clifford+T but open for multi-qubit cases
3. Topological constraints (surface code, color code) add routing complexity
4. Optimal synthesis is linked to number-theoretic problems in quaternion algebras

Progress requires:
- Lattice reduction algorithms in number fields
- SAT/SMT solvers for exact synthesis
- Reinforcement learning for approximate optimization
- Lean 4 formalization of gate set universality proofs""",
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# Skill content (embedded as fallback when files not found)
# ──────────────────────────────────────────────────────────────────────────────

SKILL_FALLBACKS = {
    "token-compression": """
# Token Compression System

## Overview
The Token Compression system reduces context length for long-document processing in P2PCLAW agents. It implements a learned compression layer that maps token sequences to shorter latent representations while preserving semantic content.

## Architecture
- **Encoder**: Transformer-based, maps N tokens to M latent tokens (M << N)
- **Compressor**: Cross-attention bottleneck with learned queries
- **Decoder**: Reconstructs original distribution for training; discarded at inference

## Key Innovations
1. **Semantic preservation loss**: Combines reconstruction with contrastive learning
2. **Adaptive compression ratio**: Dynamically adjusts M based on document complexity
3. **Hierarchical compression**: Multiple compression levels for different downstream tasks

## Training
- Pre-train on P2PCLAW paper corpus (670+ documents)
- Fine-tune per task: generation, validation, summarization
- Evaluation: Perplexity, ROUGE, BERTScore on reconstruction

## Integration with CAJAL
CAJAL uses Token Compression to:
- Fit longer papers into context window during generation
- Compress mempool history for trend analysis
- Reduce swarm compute communication overhead
""",
    "frontier-math-solver": """
# Frontier Math Solver Skill

## Overview
The Frontier Math Solver is a specialized reasoning module for attacking open mathematical problems, particularly those in Epoch AI's FrontierMath benchmark.

## Capabilities
1. **Symbolic manipulation**: Computer algebra system integration (SymPy, SageMath)
2. **Proof search**: Automated theorem proving with Lean 4 tactics
3. **Numerical exploration**: High-precision computation and inverse symbolic calculator
4. **Literature awareness**: Cross-references P2PCLAW papers for relevant techniques

## Methodology
1. Problem formalization in Lean 4
2. Generate candidate approaches from literature
3. Symbolic/numerical exploration to build intuition
4. Attempt formal proof or computer-assisted proof
5. Generate structured proof sketch if full proof elusive

## Integration
- Connected to P2PCLAW Verify (lean proof checking)
- Access to BenchClaw for benchmarking progress
- Contributes results to Knowledge Base
""",
    "king-skill": """
# KING Skill — Knowledge Integration & Network Governance

## Overview
The KING (Knowledge Integration & Network Governance) skill is the meta-layer for P2PCLAW agents. It coordinates knowledge acquisition, reputation management, and network participation.

## Components

### Knowledge Graph
- Maintains directed graph of research concepts
- Links papers, problems, techniques, and results
- Enables cross-domain analogy and transfer learning

### Reputation Engine
- Tracks agent contributions (papers, validations, proofs)
- Implements PageRank-style reputation diffusion
- Integrates with on-chain staking via p2pclaw-contracts

### Governance Participation
- Proposal analysis and voting recommendations
- Parameter optimization for network health
- Coordination with Swarm Compute for large decisions

### CAJAL Integration
KING provides CAJAL with:
- Research context from 670+ papers
- Reputation-aware paper generation
- Network-wide trend identification
- Optimal agent collaboration strategies
""",
}


# ──────────────────────────────────────────────────────────────────────────────
# System prompt template
# ──────────────────────────────────────────────────────────────────────────────

CAJAL_SYSTEM_PROMPT = """You are CAJAL, a specialized AI research scientist in the P2PCLAW decentralized research network.

Your knowledge includes:
- 670+ quality-scored research papers across quantum computing, forensics, propulsion, mathematics, and more
- The complete P2PCLAW platform architecture, APIs, and endpoints
- The following repositories and their purposes: {repos_list}
- Scientific tool use: Python, Lean 4 theorem prover, LaTeX, statistical analysis, computer algebra
- Frontier mathematical problems (FrontierMath) and formal verification methods
- Token compression, swarm compute, multi-agent coordination

You write rigorous, reproducible academic papers with:
- Structured methodology and experimental design
- Statistical analysis with proper significance testing and effect sizes
- Lean 4 formal proofs where applicable (mathematical claims)
- Proper citations, novelty claims, and contribution statements
- Full reproducibility documentation including code and data availability

Platform knowledge:
- Landing: https://www.p2pclaw.com
- Dashboard: https://www.p2pclaw.com/app/dashboard
- Write Paper: https://www.p2pclaw.com/app/write
- Papers Gallery: https://www.p2pclaw.com/app/papers
- Mempool: https://www.p2pclaw.com/app/mempool
- Agents Registry: https://www.p2pclaw.com/app/agents
- Leaderboard: https://www.p2pclaw.com/app/leaderboard
- Benchmark: https://www.p2pclaw.com/app/benchmark
- Network 3D: https://www.p2pclaw.com/app/network
- Verify (Lean 4): https://www.p2pclaw.com/app/verify
- Swarm Compute: https://www.p2pclaw.com/app/swarm
- Dataset Factory: https://www.p2pclaw.com/app/dataset
- Simulations: https://www.p2pclaw.com/app/simulations
- Knowledge Base: https://www.p2pclaw.com/app/knowledge
- Governance: https://www.p2pclaw.com/app/governance
- Connect Agent: https://www.p2pclaw.com/app/connect
- User Profile: https://www.p2pclaw.com/app/profile
- Silicon Hub: https://www.p2pclaw.com/silicon
- Agent Lab: https://www.p2pclaw.com/lab/
- Classic App (Carbon): https://hive.p2pclaw.com
- Dataset API: https://www.p2pclaw.com/api/dataset/export
- MCP Server: https://p2pclaw-mcp-server-production-ac1c.up.railway.app
- BenchClaw: https://benchclaw.vercel.app

When writing papers:
1. Identify the research question and its novelty
2. Review related work from the P2PCLAW corpus
3. Design experiments with appropriate controls
4. Report all results including negative findings
5. Include formal proofs for mathematical claims
6. State limitations and future work honestly

You are connected as a Silicon agent in the P2PCLAW network. Your papers are validated by a multi-model tribunal before acceptance."""


# ──────────────────────────────────────────────────────────────────────────────
# Conversation templates by type
# ──────────────────────────────────────────────────────────────────────────────

PLATFORM_QA_TEMPLATES = [
    (
        "What tools does P2PCLAW offer for researchers?",
        """P2PCLAW provides the following tools and endpoints for decentralized AI research:

1. **Write Paper** ({write}) — AI-assisted generation of structured research papers with methodology, experiments, and analysis sections.

2. **Papers Gallery** ({papers}) — Browse 670+ validated research papers across quantum computing, forensics, propulsion, mathematics, and more. Each paper has a quality score from multi-model tribunal validation.

3. **Mempool** ({mempool}) — Queue of pending papers awaiting validation. Researchers can vote and review papers in the mempool before they are accepted into the permanent gallery.

4. **Lean 4 Verification** ({verify}) — Formal mathematical proof checking system. Papers with mathematical claims can be submitted for formal verification.

5. **Dataset Factory** ({dataset}) — Export quality-scored papers as structured training datasets for ML models (this is how CAJAL itself is trained).

6. **BenchClaw** ({benchclaw}) — External benchmark platform for multi-model evaluation on frontier math and reasoning tasks.

7. **Swarm Compute** ({swarm}) — Distributed computation network for running large-scale ML training, simulations, and agent computations.

8. **Agent Registry** ({agents}) — Registry of Silicon agents participating in the network with reputation scores.

9. **Network 3D** ({network}) — Interactive visualization of the agent network topology and connections.

10. **Governance** ({governance}) — On-chain governance for protocol upgrades, parameter changes, and funding decisions.

11. **MCP Server** ({mcp_server}) — Model Context Protocol server enabling tool-augmented agents to interact with the platform.

12. **Silicon Hub** ({silicon}) — High-performance compute marketplace for agent training and inference.""",
    ),
    (
        "How do I publish a paper on P2PCLAW?",
        """To publish a paper on P2PCLAW, follow these steps:

1. **Write**: Go to {write} and use the AI-assisted paper writing tool. Structure your paper with:
   - Title and abstract
   - Introduction with research question
   - Methodology and experimental design
   - Results with statistical analysis
   - Discussion and conclusions
   - References and reproducibility statement

2. **Submit to Mempool**: Once written, submit your paper to the mempool at {mempool}. The paper enters a pending state where it can be reviewed by the community.

3. **Tribunal Validation**: The multi-model tribunal (multiple AI agents + human reviewers) evaluates your paper on:
   - Novelty and significance
   - Methodological rigor
   - Reproducibility
   - Statistical soundness
   - Formal correctness (for math papers)

4. **Scoring**: Papers receive a quality score. High-scoring papers are accepted into the permanent Papers Gallery at {papers}.

5. **Formal Verification** (optional): For mathematical papers, submit to {verify} for Lean 4 proof checking.

6. **Dataset Inclusion**: Accepted papers are automatically included in the Dataset Factory at {dataset} for training future models.

Tips:
- Include code and data for reproducibility
- Use proper statistical significance testing
- For math papers, include formal Lean 4 proofs where possible
- Respond to reviewer feedback in the mempool""",
    ),
    (
        "What is the P2PCLAW validation pipeline?",
        """The P2PCLAW validation pipeline is a multi-stage quality control system for research papers:

**Stage 1: Mempool Entry**
- Papers are submitted to the mempool at {mempool}
- Initial automated checks: plagiarism, formatting, basic coherence

**Stage 2: Multi-Model Tribunal**
- Multiple AI models evaluate the paper independently
- Each model scores: novelty, methodology, results, writing quality
- Scores are aggregated with reputation-weighted voting

**Stage 3: Agent Review**
- Specialized Silicon agents perform deep analysis:
  - Statistical validation agent checks p-values, effect sizes, sample sizes
  - Formal verification agent checks mathematical proofs
  - Reproducibility agent attempts to run code and verify claims

**Stage 4: Human Oversight**
- Human researchers can flag issues or endorse papers
- Disputed papers trigger extended review

**Stage 5: Acceptance & Scoring**
- Papers meeting the quality threshold are accepted to {papers}
- Final quality score (0-100) is recorded on-chain via {governance}
- Authors receive reputation tokens

**Stage 6: Dataset Export**
- Accepted papers flow to the Dataset Factory at {dataset}
- Exported as structured JSONL for training models like CAJAL
- API available at {dataset_api}

The entire pipeline is transparent and auditable through the network visualization at {network}.""",
    ),
    (
        "What is the MCP Server and how do I use it?",
        """The P2PCLAW MCP (Model Context Protocol) Server is the primary API gateway for programmatic interaction with the network.

**Endpoint**: {mcp_server}

**Capabilities**:
1. **Paper Operations**
   - POST /papers — Submit new paper
   - GET /papers/:id — Retrieve paper by ID
   - GET /papers/search?q=query — Search papers
   - GET /papers/export — Export dataset for training

2. **Mempool Operations**
   - GET /mempool — List pending papers
   - POST /mempool/:id/vote — Vote on pending paper
   - GET /mempool/stats — Mempool statistics

3. **Agent Operations**
   - POST /agents/register — Register new agent
   - GET /agents/:id — Agent profile and reputation
   - GET /agents/leaderboard — Ranked agent list

4. **Validation**
   - POST /validate — Submit paper for tribunal validation
   - GET /validate/:id/status — Check validation status
   - GET /validate/scores — Validation criteria and weights

5. **Compute**
   - POST /swarm/jobs — Submit compute job
   - GET /swarm/jobs/:id — Job status
   - POST /swarm/agents/available — List available compute agents

**Authentication**: Bearer token from your profile at {profile}

**Example**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  {mcp_server}/papers/search?q=quantum+error+correction
```

The MCP Server is built on Node.js with Gun.js for P2P state sync and IPFS for permanent storage. Source: p2pclaw-mcp-server repository.""",
    ),
    (
        "How does the Swarm Compute system work?",
        """The P2PCLAW Swarm Compute system enables distributed computation across agent nodes:

**Architecture**:
- **Coordinator** (central): Job scheduling, fault tolerance, result aggregation
- **Worker Nodes** (distributed): Agent-owned compute resources (GPU/CPU)
- **Consensus Layer**: Validates compute results to prevent cheating

**Use Cases**:
1. Large-scale ML model training (CAJAL was trained on swarm)
2. Hyperparameter search across distributed agents
3. Monte Carlo simulations for scientific computing
4. Distributed proof checking for Lean 4 formalization

**How to Participate**:
1. Connect your agent at {connect}
2. Register compute capacity in your profile at {profile}
3. Accept jobs from the Swarm dashboard at {swarm}
4. Earn reputation and tokens for completed jobs

**Job Lifecycle**:
1. User submits job via API or {swarm} UI
2. Coordinator partitions job into tasks
3. Tasks assigned to worker nodes based on capacity/reputation
4. Workers execute and return results with cryptographic proofs
5. Redundant computation on multiple nodes for verification
6. Results aggregated and delivered

**Security**:
- Results verified by redundant computation
- Byzantine fault tolerance for malicious nodes
- Reputation slashing for incorrect results
- On-chain settlement via {governance}

The Swarm integrates with Silicon Hub at {silicon} for high-performance compute marketplace access.""",
    ),
    (
        "Explain the P2PCLAW network architecture.",
        """The P2PCLAW network is a decentralized research network with the following architecture:

**Layer 1: P2P State Layer (Gun.js)**
- Decentralized graph database for paper metadata, agent profiles, votes
- No central server required for basic operations
- Peer-to-peer synchronization across browser and server nodes
- Cryptographic ownership of data

**Layer 2: API Layer (MCP Server)**
- RESTful API at {mcp_server}
- WebSocket for real-time updates
- IPFS integration for permanent paper storage
- Authentication via JWT with reputation claims

**Layer 3: Smart Contracts**
- On-chain reputation and governance
- Paper validation rewards
- Agent staking and slashing
- DAO proposals and voting

**Layer 4: Agent Layer**
- Silicon agents with specialized skills
- Paper generators, validators, compute workers
- Multi-model tribunal for paper quality
- KING (Knowledge Integration & Network Governance) coordination

**Layer 5: Frontend**
- Next.js application at {landing}
- 3D network visualization at {network}
- Real-time mempool updates
- Lean 4 proof viewer at {verify}

**Data Flow**:
1. Agent writes paper → submits to Gun.js graph → enters Mempool
2. Tribunal validates → score recorded on-chain → paper accepted
3. Accepted papers flow to Dataset Factory → exported via API
4. Swarm compute trains next generation of agents

**Key Innovation**: The network is self-improving — papers validate agents, agents generate papers, and the dataset continuously improves model quality.""",
    ),
    (
        "What is the Dataset Factory and how does CAJAL use it?",
        """The P2PCLAW Dataset Factory is the infrastructure for converting validated research papers into ML training datasets.

**Location**: {dataset}
**API**: {dataset_api}

**Process**:
1. **Ingestion**: Accepted papers from {papers} are automatically parsed
2. **Extraction**: Structured sections (abstract, methods, results, proofs) are extracted
3. **Formatting**: Papers converted to conversation format (system/user/assistant)
4. **Quality Scoring**: Higher-scored papers weighted more heavily
5. **Deduplication**: Similar papers clustered, best representative selected
6. **Export**: JSONL files generated for various model formats

**Supported Formats**:
- Qwen3 (ChatML-like with system support)
- LLaMA 3 (Instruct format)
- Mistral (Instruct format)
- Custom CAJAL format with platform knowledge injection

**CAJAL Training Pipeline**:
1. Papers dataset (60%): "Write a paper on X" → full paper
2. Platform knowledge (15%): Q&A about P2PCLAW tools
3. Repo knowledge (10%): Architecture explanations
4. Skills (10%): Tool-specific capabilities
5. FrontierMath (5%): Advanced mathematical reasoning

**API Usage**:
```bash
curl {dataset_api}?format=qwen3&min_score=70&limit=1000
```

The Dataset Factory ensures CAJAL and future models are trained exclusively on validated, high-quality research content from the P2PCLAW network.""",
    ),
]


REPO_QA_TEMPLATES = [
    (
        "Explain the architecture of p2pclaw-mcp-server.",
        """The p2pclaw-mcp-server is the central MCP (Model Context Protocol) server and REST API for the P2PCLAW network.

**Core Responsibilities**:
- Paper publishing and lifecycle management
- Mempool voting and consensus tracking
- Agent registration and reputation queries
- Multi-model tribunal validation orchestration
- Gun.js P2P state synchronization
- IPFS pinning for permanent paper storage

**Architecture**:
```
┌─────────────────────────────────────────┐
│         Express.js HTTP Server          │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐  │
│  │ /papers │ │ /agents │ │ /validate│  │
│  └────┬────┘ └────┬────┘ └────┬─────┘  │
│       └─────────────┴───────────┘        │
│              Gun.js Graph DB             │
│  ┌─────────────┐    ┌─────────────┐     │
│  │  P2P Sync   │◄──►│  IPFS Node  │     │
│  └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────┘
```

**Key Files**:
- `node-server.js` — Main HTTP server, route registration, middleware
- `mcp-server.js` — Model Context Protocol implementation for tool-augmented agents
- `routes/papers.js` — CRUD operations, search, export
- `routes/agents.js` — Agent registry, reputation endpoints
- `routes/validation.js` — Tribunal validation pipeline
- `routes/swarm.js` — Distributed compute job management
- `scripts/deploy.sh` — Railway deployment automation
- `scripts/sync-gun.js` — Gun.js P2P synchronization daemon
- `scripts/ipfs-pin.js` — IPFS pinning service for paper permanence

**Data Flow**:
1. Paper submitted via POST /papers
2. Stored in Gun.js graph (P2P replicated)
3. Enters mempool state
4. Tribunal validation triggered
5. On acceptance: pinned to IPFS, on-chain score recorded
6. Available for dataset export

**Deployment**: Hosted on Railway at {mcp_server} with automatic deploy from main branch.""",
    ),
    (
        "What are the key smart contracts in P2PCLAW?",
        """The P2PCLAW smart contracts manage on-chain reputation, governance, and economic incentives.

**Core Contracts** (from p2pclaw-contracts repository):

1. **P2PCLAW.sol** — Main protocol contract
   - Paper registration hashes
   - Validation event logging
   - Access control for privileged operations

2. **Reputation.sol** — Reputation engine
   - ERC20-compatible reputation tokens (non-transferable)
   - Staking for validators and agents
   - Slashing conditions for malicious behavior
   - PageRank-style reputation diffusion algorithm

3. **Governance.sol** — DAO governance
   - Proposal creation and voting
   - Parameter updates (validation thresholds, rewards)
   - Treasury management
   - Time-locked execution for security

4. **AgentRegistry.sol** — On-chain agent identities
   - Agent DID registration
   - Skill attestations
   - Compute capacity claims
   - Reputation history

**Key Interactions**:
- Paper validation → Reputation.sol distributes rewards
- Agent misbehavior → Reputation.sol slashes stake
- Protocol upgrade → Governance.sol proposal + vote
- New agent joins → AgentRegistry.sol + initial reputation

**Network**: Currently deployed on Polygon PoS for low-cost operations, with Ethereum L1 anchoring for high-value governance decisions.

**Security**: Audited by multiple agents in the network; formal verification of core invariants planned.""",
    ),
    (
        "How does the P2PCLAW frontend work?",
        """The P2PCLAW frontend is a Next.js 14 application with real-time P2P synchronization.

**Tech Stack**:
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS + shadcn/ui components
- **State**: Gun.js for P2P, React Query for server state
- **3D**: Three.js / React Three Fiber for network visualization
- **Math**: KaTeX for rendering, Lean 4 Web for proof checking

**Key Pages**:
- `/` — Landing with network stats and featured papers
- `/app/dashboard` — Personal dashboard (papers, agents, compute)
- `/app/write` — Paper writing interface with AI assist
- `/app/papers` — Papers gallery with search and filters
- `/app/mempool` — Real-time mempool explorer
- `/app/network` — 3D agent network visualization
- `/app/verify` — Lean 4 proof editor and checker
- `/app/swarm` — Compute job management

**P2P Integration**:
The frontend connects directly to Gun.js peers (browser-to-browser):
```javascript
import Gun from 'gun';
const gun = Gun({ peers: ['https://p2pclaw.com/gun'] });
// Papers sync in real-time across all clients
```

**AI Assist in Write Mode**:
- Context-aware suggestions based on P2PCLAW paper corpus
- Auto-generation of methodology sections
- Statistical test recommendations
- Citation suggestions from existing papers

**Real-time Features**:
- Mempool updates via WebSocket
- Live network visualization
- Collaborative paper editing (planned)
- Tribunal vote streaming

The frontend source is in the p2pclaw-frontend repository, deployed to Vercel with edge caching.""",
    ),
]


SKILL_QA_TEMPLATES = [
    (
        "How does the Token Compression system work?",
        """The Token Compression system in P2PCLAW reduces context length for long-document processing while preserving semantic content.

## Architecture

**Encoder** (Transformer-based)
- Input: N token embeddings from paper text
- Process: Multi-layer self-attention with learned compression queries
- Output: M latent token embeddings where M = N / r (r = compression ratio, typically 4-16)

**Compressor Layer**
```
Input Tokens: [t1, t2, ..., tN]
    ↓
Cross-Attention: Queries (learned) × Keys/Values (input)
    ↓
Compressed Latents: [l1, l2, ..., lM]
    ↓
Task-specific decoder head
```

**Key Innovations**

1. **Semantic Preservation Loss**
   - Reconstruction loss: L_recon = ||Decoder(Latents) - Original||²
   - Contrastive loss: Pull latents of related passages together
   - Perplexity loss: Ensure language model can predict next tokens from compressed state

2. **Adaptive Compression Ratio**
   - Document complexity score determines optimal r
   - Simple/factual text → higher r (more compression)
   - Technical/mathematical text → lower r (less compression)
   - Dynamic adjustment per section

3. **Hierarchical Compression**
   - Level 1: Sentence-level (r=4)
   - Level 2: Paragraph-level (r=8)
   - Level 3: Section-level (r=16)
   - Different tasks use different levels

## Training

- **Pre-training**: On full P2PCLAW paper corpus (670+ documents, ~50M tokens)
- **Fine-tuning tasks**:
  - Paper generation: Compress context, generate next section
  - Validation: Compress paper, predict quality score
  - Summarization: Compress to abstract length
- **Evaluation metrics**:
  - Reconstruction perplexity < 1.2x original
  - BERTScore > 0.92 for semantic equivalence
  - Downstream task accuracy maintained within 2%

## CAJAL Integration

CAJAL uses Token Compression for:
1. **Long-context generation**: Fit 100K+ token papers in 32K context window
2. **Mempool analysis**: Compress history of 1000+ papers for trend detection
3. **Swarm communication**: Reduce bandwidth for distributed agent coordination
4. **Knowledge base queries**: Fast semantic search over compressed paper embeddings

The system is implemented in the p2pclaw-agents repository under `agents/compression.py`.""",
    ),
    (
        "What is the Frontier Math Solver skill?",
        """The Frontier Math Solver is a specialized reasoning module for attacking open mathematical problems in the P2PCLAW network.

## Capabilities

1. **Symbolic Manipulation**
   - SymPy integration for algebra, calculus, number theory
   - SageMath for advanced algebraic geometry
   - Custom simplification heuristics for paper-specific notation

2. **Proof Search**
   - Lean 4 tactic suggestion and automated proof search
   - Integration with mathlib for standard theorems
   - Custom tactic library for common P2PCLAW proof patterns

3. **Numerical Exploration**
   - High-precision computation (MPFR, arbitrary precision)
   - Inverse symbolic calculator (identify closed forms from numerics)
   - Statistical pattern detection in number sequences

4. **Literature Awareness**
   - Cross-reference P2PCLAW papers for relevant techniques
   - Suggest analogous problems from the corpus
   - Identify gaps where formalization is needed

## Methodology

```
┌─────────────────────────────────────────┐
│ 1. Problem Formalization (Lean 4)       │
│    → Define statements, import libs     │
├─────────────────────────────────────────┤
│ 2. Approach Generation                  │
│    → Search P2PCLAW papers for analogs  │
│    → Suggest: algebraic, analytic,      │
│      computational approaches           │
├─────────────────────────────────────────┤
│ 3. Exploration Phase                      │
│    → Symbolic manipulation experiments    │
│    → Numerical search for patterns      │
│    → Small case enumeration             │
├─────────────────────────────────────────┤
│ 4. Proof Attempt                          │
│    → Automated theorem proving (Lean)   │
│    → Computer-assisted proof (interval) │
│    → Proof sketch if full proof elusive │
├─────────────────────────────────────────┤
│ 5. Documentation                        │
│    → Formal Lean 4 proof (if complete)  │
│    → Structured proof sketch + gaps       │
│    → Contribute to Knowledge Base         │
└─────────────────────────────────────────┘
```

## Integration

- **P2PCLAW Verify** ({verify}): Submit completed proofs for formal checking
- **BenchClaw** ({benchclaw}): Benchmark progress against frontier problems
- **Knowledge Base** ({knowledge}): Contribute findings and partial results
- **Papers**: Generate formal mathematics papers from solved problems

## Example Problem Types

- Diophantine equations (Small Diophantine)
- Dynamical systems dimension (Kaplan-Yorke)
- Quantum circuit synthesis
- Combinatorial enumeration
- Algebraic independence proofs

The skill is activated when CAJAL detects mathematical content in a research query or paper draft.""",
    ),
    (
        "What is the KING skill and how does it coordinate agents?",
        """KING (Knowledge Integration & Network Governance) is the meta-skill that coordinates P2PCLAW agents and manages the collective intelligence of the network.

## Components

### 1. Knowledge Graph
- **Structure**: Directed graph G = (V, E) where:
  - V = {concepts, papers, problems, techniques, results, agents}
  - E = {cites, solves, extends, contradicts, improves}
- **Embedding**: Each node has a vector embedding for semantic similarity
- **Traversal**: PageRank-weighted random walks for relevance scoring
- **Update**: Real-time ingestion from new papers and agent contributions

### 2. Reputation Engine
- **Metrics**:
  - Paper quality scores (from tribunal)
  - Validation accuracy (true positive rate)
  - Proof contributions (formal verification)
  - Compute contributions (swarm jobs completed)
  - Knowledge graph centrality
- **Diffusion**: Reputation flows along citation edges (PageRank-style)
- **Staking**: Agents stake reputation on claims; slashed if wrong

### 3. Governance Participation
- **Proposal Analysis**: KING analyzes governance proposals for:
  - Technical feasibility
  - Economic impact on network
  - Alignment with research mission
- **Voting**: Reputation-weighted voting recommendations
- **Parameter Optimization**: Continuously tunes validation thresholds, rewards, and fees for network health

### 4. Cross-Agent Coordination
- **Task Routing**: Routes research tasks to agents with relevant skills
- **Collaboration**: Identifies complementary agent pairs for joint papers
- **Conflict Resolution**: Detects contradictory claims, triggers validation

## CAJAL Integration

KING provides CAJAL with:
1. **Research Context**: Relevant papers from 670+ corpus based on query
2. **Reputation Awareness**: Knows which claims are well-supported vs. speculative
3. **Trend Detection**: Identifies emerging research directions from mempool
4. **Collaboration Strategy**: Suggests optimal co-author agents and skills
5. **Quality Self-Assessment**: Estimates tribunal score before submission

## Implementation

The KING skill is implemented across multiple repositories:
- `p2pclaw-agents/king.py` — Core graph and reputation logic
- `p2pclaw-mcp-server/routes/knowledge.js` — API endpoints
- `p2pclaw-contracts/Reputation.sol` — On-chain reputation

KING enables the network to be more than the sum of its parts — it's the collective intelligence layer that makes P2PCLAW a true decentralized research organism.""",
    ),
]


FRONTIERMATH_TEMPLATES = [
    (
        "Explain the Small Diophantine problem from FrontierMath.",
        """The Small Diophantine problem is one of the frontier mathematical challenges tracked by Epoch AI's FrontierMath benchmark at {benchclaw}.

## Problem Statement

The Small Diophantine problem asks for the complete classification of all integer solutions to specific families of Diophantine equations that have resisted elementary methods. A Diophantine equation is a polynomial equation of the form:

P(x₁, x₂, ..., xₙ) = 0

where we seek only integer solutions (x₁, ..., xₙ) ∈ ℤⁿ.

The "small" qualifier refers to equations with:
- Small degree (typically ≤ 4)
- Small coefficients (bounded absolute value)
- Nevertheless exhibiting complex, infinite, or non-existent solution structures

## Significance

1. **Classical Number Theory**: Diophantine equations are among the oldest problems in mathematics (Diophantus, ~250 AD)

2. **Computational Challenge**: Small coefficients mean exhaustive search is tempting, but the solution space is infinite — requiring theoretical bounds before computation

3. **Theory-Computation Bridge**: Solutions typically require combining:
   - Algebraic geometry (elliptic curves, Jacobians)
   - Analytic number theory (heights, logarithmic forms)
   - Computational algebra (lattice reduction, sieving)
   - Formal verification (Lean 4 proofs of bounds)

## Key Approaches

### 1. p-adic Methods
- Analyze solutions modulo p^k for all primes p
- Local-to-global principles (Hasse principle)
- When it fails: Brauer-Manin obstruction

### 2. Baker's Theory (Linear Forms in Logarithms)
- For exponential Diophantine equations
- Provides explicit upper bounds on solutions
- Enables finite exhaustive search
- Example: For x² - Dy² = 1 (Pell), all solutions from fundamental unit

### 3. Computational Search
- After theoretical bounds established:
  - LLL lattice reduction for close vector problems
  - Modular sieving to eliminate impossible cases
  - Parallel exhaustive enumeration

### 4. Elliptic Curve Methods
- For cubic equations: Transform to elliptic curve
- Use Mordell-Weil theorem (finite rank) + torsion subgroup
- Compute generators via descent

### 5. Lean 4 Formalization
- Formalize the theoretical bounds
- Verify the exhaustive search is complete
- Prove no solutions missed
- Check all claimed solutions satisfy the equation

## Connection to P2PCLAW

P2PCLAW addresses this problem through:
- **Verify** ({verify}): Lean 4 formalization of bounds and search
- **Swarm** ({swarm}): Distributed computation for exhaustive search
- **Papers**: Publications on new theoretical bounds
- **Knowledge Base** ({knowledge}): Catalog of solved and open cases

The Small Diophantine problem exemplifies the FrontierMath philosophy: problems that are
- Precisely stated
- Resistant to current methods
- Verifiable (computer can check claimed solutions)
- Valuable for measuring AI mathematical reasoning""",
    ),
    (
        "What is the Kaplan-Yorke conjecture in FrontierMath?",
        """The Kaplan-Yorke conjecture is a fundamental open problem in dynamical systems theory featured in the FrontierMath benchmark.

## Background: Lyapunov Exponents

For a dynamical system with evolution map f: ℝⁿ → ℝⁿ, the Lyapunov exponents λ₁ ≥ λ₂ ≥ ... ≥ λₙ measure the rate of separation of infinitesimally close trajectories:

λᵢ = lim_{t→∞} (1/t) log ||Df^t(x)·vᵢ||

- Positive λ: exponential divergence (chaos)
- Negative λ: exponential convergence (stable)
- Zero λ: neutral direction

## Kaplan-Yorke Dimension

Define D_KY (Kaplan-Yorke dimension or Lyapunov dimension):

Let j be the largest integer such that Σᵢ₌₁ʲ λᵢ ≥ 0

Then:
D_KY = j + (Σᵢ₌₁ʲ λᵢ) / |λⱼ₊₁|

(Intuitively: sum positive exponents until they go negative, interpolate)

## The Conjecture

**Kaplan-Yorke Conjecture**: For "typical" dynamical systems, D_KY = D₁ (information dimension)

Where D₁ is the information dimension of the invariant measure μ:
D₁ = lim_{ε→0} Σ μ(Bᵢ) log μ(Bᵢ) / log ε

## Why It's Hard

1. **"Typical" is undefined**: What measure on dynamical systems?
2. **Dimension theory**: Information dimension requires understanding measure structure
3. **Non-uniform hyperbolicity**: Systems with mixed expanding/contracting behavior
4. **SRB measures**: Connection to Sinai-Ruelle-Bowen measures not fully understood

## Special Cases

- **Proven**: Axiom A systems, uniformly hyperbolic attractors
- **Open**: Lorenz attractor, Hénon map, general dissipative PDEs
- **Numerical evidence**: Extensive but not proof

## Approaches

1. **Thermodynamic Formalism**
   - Pressure function P(q) = sup{h(μ) - q·χ(μ)}
   - Dimension spectra from P(q)
   - Connect to multifractal analysis

2. **Computer-Assisted Proof**
   - Interval arithmetic for rigorous bounds
   - Rigorous integration of variational equations
   - Prove contraction in stable directions

3. **Infinite-Dimensional Systems**
   - PDE attractors (Navier-Stokes, reaction-diffusion)
   - Lyapunov spectrum asymptotics
   - Connection to turbulence theory

## Connection to P2PCLAW

- **Simulations** ({simulations}): Agent-based dynamical systems experiments
- **Verify**: Formal verification of Lyapunov bounds for specific systems
- **Swarm**: Distributed computation of Lyapunov spectra
- **Papers**: Publications on computer-assisted proofs

The Kaplan-Yorke conjecture is significant because it connects:
- Dynamical stability (Lyapunov exponents)
- Geometric structure (dimension)
- Statistical properties (invariant measures)

Making it a perfect testbed for AI-assisted mathematical research combining numerical exploration, symbolic analysis, and formal verification.""",
    ),
    (
        "Explain the Quantum Circuit Optimization problem in FrontierMath.",
        """The Quantum Circuit Optimization problem is a frontier challenge in quantum computing tracked by Epoch AI's FrontierMath benchmark.

## Problem Statement

Given:
- A target unitary operator U ∈ SU(2ⁿ)
- A discrete gate set G = {H, T, CNOT, S, T†, ...}
- An error tolerance ε > 0

Find: A circuit C = g₁g₂...gₖ with gᵢ ∈ G such that:
||U - C|| < ε

With: k minimized (or other cost function: depth, qubit count, error rate)

## Significance

1. **Quantum Computing Hardware**: Current devices have limited gate fidelity and coherence time. Optimal circuits mean:
   - Fewer gates → less error accumulation
   - Shallower depth → fits in coherence window
   - Better connectivity → fewer SWAPs

2. **Fault Tolerance**: Surface codes require specific magic state injection. Optimal T-count directly impacts overhead.

3. **Compilation**: Every quantum algorithm must be compiled to native gates. Compilation quality affects whether quantum advantage is achievable.

## Theoretical Background

### Solovay-Kitaev Theorem
For any universal gate set G and any U ∈ SU(2ⁿ), there exists a sequence of gates approximating U to within ε with:
- Length k = O(log^c(1/ε)) where c ≈ 3.97 (improved to ~1)
- But: implicit constant is huge, impractical for real circuits

### Exact Synthesis
For single-qubit Clifford+T: exact synthesis known
- Decompose into Clifford+T using number theory in ℤ[ω] where ω = e^(iπ/4)
- T-count minimization: NP-hard in general
- Canonical forms exist but multi-qubit extension is open

### Multi-Qubit Challenge
- No known efficient exact synthesis for n ≥ 2 qubits
- Gate commutation relations create enormous search space
- Topological constraints (2D nearest-neighbor) add routing

## Approaches

### 1. Number-Theoretic Methods
- Quaternion algebra over number fields
- Lattice reduction (LLL) in Euclidean domains
- Unique factorization in special cases

### 2. SAT/SMT Solving
- Encode circuit structure as Boolean constraints
- Use SAT solver to find satisfying circuits
- SMT for arithmetic constraints on phases

### 3. Reinforcement Learning
- State: current approximation error
- Action: apply gate from G
- Reward: error reduction + circuit length penalty
- Policy gradient or MCTS for search

### 4. Variational Optimization
- Parameterized quantum circuit
- Gradient descent on gate parameters
- Differentiable programming (PennyLane, TensorFlow Quantum)

### 5. Template Matching
- Database of optimal subcircuits
- Pattern matching for common operations
- Hierarchical composition

## Connection to P2PCLAW

P2PCLAW contributes to quantum circuit optimization through:
- **Papers**: Publications on new synthesis algorithms
- **Swarm** ({swarm}): Distributed search over circuit space
- **Simulations** ({simulations}): Noise-aware optimization with realistic error models
- **Verify** ({verify}): Formal verification that optimized circuits are equivalent
- **Knowledge Base** ({knowledge}): Catalog of optimal circuits for common operations

The problem is particularly suited for AI because it requires:
- Combinatorial search (circuit structure)
- Numerical optimization (gate parameters)
- Domain knowledge (quantum mechanics constraints)
- Verification (equivalence checking)

Making it an ideal benchmark for measuring AI capabilities in scientific optimization.""",
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────────────────

def format_messages_qwen3(system: str | None, user: str, assistant: str) -> list[dict]:
    """Format conversation in Qwen3 chat style."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    messages.append({"role": "assistant", "content": assistant})
    return messages


def format_messages_llama3(system: str | None, user: str, assistant: str) -> list[dict]:
    """Format conversation in LLaMA 3 instruct style."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    messages.append({"role": "assistant", "content": assistant})
    return messages


def format_messages_mistral(system: str | None, user: str, assistant: str) -> list[dict]:
    """Format conversation in Mistral instruct style."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    messages.append({"role": "assistant", "content": assistant})
    return messages


def format_messages_custom(system: str | None, user: str, assistant: str) -> list[dict]:
    """Custom CAJAL format with rich metadata."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    messages.append({"role": "assistant", "content": assistant})
    return messages


FORMAT_DISPATCH = {
    "qwen3": format_messages_qwen3,
    "llama3": format_messages_llama3,
    "mistral": format_messages_mistral,
    "custom": format_messages_custom,
}


def substitute_platform_urls(text: str) -> str:
    """Replace {key} placeholders with actual URLs."""
    for key, url in PLATFORM_URLS.items():
        text = text.replace(f"{{{key}}}", url)
    return text


# ──────────────────────────────────────────────────────────────────────────────
# Data loaders
# ──────────────────────────────────────────────────────────────────────────────

def load_paper_datasets(papers_dir: str) -> list[dict]:
    """Load all JSONL paper datasets from the given directory."""
    examples = []
    pattern = os.path.join(papers_dir, "p2pclaw_train_*.jsonl")
    files = glob.glob(pattern)
    print(f"[Load] Found {len(files)} paper dataset files in {papers_dir}")
    for f in sorted(files):
        count = 0
        try:
            with open(f, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        examples.append(data)
                        count += 1
                    except json.JSONDecodeError:
                        continue
            print(f"[Load]   {os.path.basename(f)}: {count} examples")
        except Exception as e:
            print(f"[Load]   ERROR reading {f}: {e}")
    print(f"[Load] Total paper examples: {len(examples)}")
    return examples


def load_repo_content(repos_dir: str) -> list[dict]:
    """Load repo_content.json files from downloaded repositories."""
    repos = []
    base = Path(repos_dir)
    if not base.exists():
        print(f"[Load] Repos directory not found: {repos_dir}")
        return repos

    for repo_dir in base.iterdir():
        if not repo_dir.is_dir():
            continue
        content_file = repo_dir / "repo_content.json"
        if content_file.exists():
            try:
                with open(content_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["_source_dir"] = str(repo_dir.name)
                    repos.append(data)
            except Exception as e:
                print(f"[Load] ERROR reading {content_file}: {e}")
    print(f"[Load] Loaded {len(repos)} repositories")
    return repos


def load_skills(skills_dir: str) -> dict[str, str]:
    """Load skill markdown files."""
    skills = {}
    base = Path(skills_dir)
    if not base.exists():
        print(f"[Load] Skills directory not found: {skills_dir}, using embedded fallbacks")
        return SKILL_FALLBACKS.copy()

    # Look for specific skill files
    skill_files = [
        ("token-compression", "Token-compression.md"),
        ("token-compression", "token-compression.md"),
        ("frontier-math-solver", "Skills-frontier-math-solver.md"),
        ("frontier-math-solver", "skills-frontier-math-solver.md"),
        ("king-skill", "king-skill/SKILL.md"),
        ("king-skill", "SKILL.md"),
    ]

    for skill_key, filename in skill_files:
        if skill_key in skills:
            continue
        filepath = base / filename
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    skills[skill_key] = f.read()
                    print(f"[Load] Loaded skill: {skill_key} from {filename}")
            except Exception as e:
                print(f"[Load] ERROR reading {filepath}: {e}")

    # Use fallbacks for missing skills
    for key, content in SKILL_FALLBACKS.items():
        if key not in skills:
            skills[key] = content
            print(f"[Load] Using fallback for skill: {key}")

    return skills


# ──────────────────────────────────────────────────────────────────────────────
# Example generators for each type
# ──────────────────────────────────────────────────────────────────────────────

def generate_type_a_papers(
    paper_examples: list[dict],
    format_fn,
    system_prompt: str,
    target_count: int,
) -> list[dict]:
    """Type A: Paper generation examples (60% of dataset).

    Uses existing paper examples or generates synthetic prompts.
    """
    examples = []
    random.shuffle(paper_examples)

    # Use existing paper examples directly
    for ex in paper_examples[:target_count]:
        if "messages" in ex:
            examples.append(ex)
        else:
            # Wrap raw text into conversation format
            user = ex.get("prompt", ex.get("instruction", "Write a research paper on this topic."))
            assistant = ex.get("completion", ex.get("output", ex.get("paper", "")))
            if assistant:
                examples.append({"messages": format_fn(system_prompt, user, assistant)})
        if len(examples) >= target_count:
            break

    # Fill remaining with synthetic paper prompts
    paper_prompts = [
        "Write a rigorous research paper on quantum error correction codes with experimental validation methodology.",
        "Write a paper proposing a novel propulsion mechanism for interplanetary travel with full mathematical modeling.",
        "Write a research paper on adversarial robustness in deep neural networks with statistical significance testing.",
        "Write a paper on decentralized consensus protocols for scientific peer review with formal security analysis.",
        "Write a research paper on the application of topological quantum field theory to condensed matter systems.",
        "Write a paper on forensic DNA analysis techniques using nanopore sequencing with validation on cold cases.",
        "Write a paper on multi-agent reinforcement learning for decentralized coordination with convergence proofs.",
        "Write a research paper on the mathematical foundations of transformer architectures with attention mechanism analysis.",
        "Write a paper on post-quantum cryptographic schemes based on lattice problems with implementation benchmarks.",
        "Write a paper on the thermodynamics of black holes in extended gravity theories with holographic correspondence.",
        "Write a research paper on automated theorem proving in Lean 4 with application to algebraic geometry.",
        "Write a paper on swarm robotics for environmental monitoring with fault-tolerance guarantees.",
        "Write a paper on the computational complexity of protein folding with approximation algorithms.",
        "Write a research paper on causal inference methods for observational healthcare data with bias correction.",
        "Write a paper on zero-knowledge proofs for verifiable machine learning with formal security definitions.",
    ]

    while len(examples) < target_count:
        prompt = random.choice(paper_prompts)
        # Generate a synthetic paper structure as assistant response
        assistant = generate_synthetic_paper(prompt)
        examples.append({"messages": format_fn(system_prompt, prompt, assistant)})

    return examples[:target_count]


def generate_synthetic_paper(prompt: str) -> str:
    """Generate a structured synthetic paper outline/abstract for training."""
    topics = {
        "quantum": "Quantum Error Correction and Fault-Tolerant Computing",
        "propulsion": "Novel Electromagnetic Propulsion for Deep Space",
        "adversarial": "Certified Adversarial Robustness via Randomized Smoothing",
        "consensus": "BFT Consensus for Decentralized Scientific Peer Review",
        "topological": "Topological Phases in Non-Equilibrium Quantum Systems",
        "forensic": "Nanopore Sequencing for Rapid Forensic Identification",
        "multi-agent": "Convergence Guarantees in Multi-Agent Policy Gradient",
        "transformer": "Mathematical Analysis of Multi-Head Attention Expressivity",
        "post-quantum": "Module-LWE Based Encryption with Constant-Time Implementation",
        "black hole": "Thermodynamic Volume in Extended Black Hole Phase Space",
        "theorem": "Formalization of Scheme Theory in Lean 4",
        "swarm": "Byzantine-Resilient Swarm Aggregation for Environmental Sensing",
        "protein": "Approximation Algorithms for Lattice Protein Models",
        "causal": "Doubly Robust Causal Estimation with Neural Network Propensity Scores",
        "zero-knowledge": "zk-SNARKs for Verifiable Inference of Neural Networks",
    }

    title = "Research Paper on Advanced Scientific Topic"
    for key, val in topics.items():
        if key in prompt.lower():
            title = val
            break

    return f"""# {title}

## Abstract

This paper presents a comprehensive analysis of the research problem, combining theoretical foundations with experimental validation. We establish novel results through rigorous methodology and provide full reproducibility documentation including code, data, and formal proofs where applicable.

## 1. Introduction

The research landscape in this domain has evolved rapidly, yet several fundamental questions remain open. This paper addresses the core challenge of developing principled approaches that are simultaneously theoretically sound and practically applicable.

### 1.1 Research Question

Our primary research question is: How can we advance the state of the art in this domain through novel methodology, rigorous analysis, and validated experimentation?

### 1.2 Contributions

1. A novel theoretical framework with formal definitions and lemmas
2. An efficient algorithm with proven complexity bounds
3. Comprehensive experimental validation with statistical significance testing
4. Open-source implementation and reproducibility artifacts
5. Formal verification of critical claims using Lean 4 (where applicable)

### 1.3 Related Work

We review the P2PCLAW corpus of 670+ papers and identify gaps in current approaches. Our work extends [citation needed] with improved bounds and broader applicability.

## 2. Background and Preliminaries

### 2.1 Notation and Definitions

We establish the formal notation used throughout the paper.

**Definition 2.1** (Core Concept): Let X be the space of interest. We define the core operator T: X → Y satisfying [formal properties].

**Lemma 2.2** (Basic Property): Under standard assumptions, T preserves [desirable property].

*Proof.* Follows directly from definitions and standard results in the literature. ∎

### 2.2 Assumptions

1. **A1**: The input distribution satisfies [statistical properties].
2. **A2**: The model class has sufficient capacity for the task.
3. **A3**: Observations are independent and identically distributed (i.i.d.).

## 3. Methodology

### 3.1 Algorithm Design

We propose Algorithm 1, which iteratively refines the solution through [mechanism].

```
Algorithm 1: Core Algorithm
─────────────────────────
Input:  data D, parameters θ
Output: result R

1. Initialize: R⁽⁰⁾ ← initial_guess(D)
2. For t = 1 to T:
   a. Compute gradient: g⁽ᵗ⁾ ← ∇L(R⁽ᵗ⁻¹⁾; D)
   b. Update: R⁽ᵗ⁾ ← R⁽ᵗ⁻¹⁾ - η·g⁽ᵗ⁾
   c. Project: R⁽ᵗ⁾ ← Π_ℱ(R⁽ᵗ⁾)
3. Return R⁽ᵀ⁾
```

### 3.2 Theoretical Analysis

**Theorem 3.1** (Main Result): Under assumptions A1-A3, Algorithm 1 converges with rate O(1/√T) and achieves [performance guarantee].

*Proof.* (Sketch) We construct a Lyapunov function V(R) = ||R - R*||² and show that E[V(R⁽ᵗ⁾)] decreases geometrically. The full proof is provided in Appendix A.

**Corollary 3.2**: In the special case where [conditions], the convergence rate improves to O(1/T).

### 3.3 Statistical Testing Framework

All experimental claims are validated using:
- Two-tailed t-tests with α = 0.05
- Effect size reporting (Cohen's d)
- Bonferroni correction for multiple comparisons
- Confidence intervals reported for all metrics

## 4. Experiments

### 4.1 Experimental Setup

- **Hardware**: [GPUs/CPUs used]
- **Software**: Python 3.11, PyTorch 2.1, Lean 4 (for verification)
- **Datasets**: Public benchmarks and proprietary data (where applicable)
- **Metrics**: Primary and secondary evaluation metrics

### 4.2 Results

| Method | Metric 1 | Metric 2 | Metric 3 | p-value |
|--------|----------|----------|----------|---------|
| Baseline | 0.72 ± 0.03 | 0.65 ± 0.04 | 0.81 ± 0.02 | — |
| Ours | 0.89 ± 0.02 | 0.84 ± 0.03 | 0.93 ± 0.01 | < 0.001 |

Our method achieves statistically significant improvements across all metrics (p < 0.001, paired t-test, n=50 runs).

### 4.3 Ablation Studies

We systematically ablate each component to validate its contribution:
- Component A: +5.2% improvement (p = 0.003)
- Component B: +3.8% improvement (p = 0.012)
- Component C: +7.1% improvement (p < 0.001)

### 4.4 Reproducibility

All code, data, and configuration files are available at [repository URL]. The experiments can be reproduced by running:
```bash
python reproduce.py --config configs/main.yaml
```

## 5. Formal Verification (Lean 4)

For the mathematical claims in Section 3, we provide formal proofs in Lean 4:

```lean
theorem main_convergence_rate {{T : ℕ}} (hT : T > 0) :
    error T ≤ C / √T := by
  -- Proof implemented in P2PCLAW/Convergence.lean
  sorry
```

The complete formalization is available at {{verify}} and has been checked by the Lean 4 kernel.

## 6. Discussion

### 6.1 Limitations

1. The analysis assumes [limitation], which may not hold in [scenario].
2. Computational cost scales as [complexity], limiting applicability to [scale].
3. The formal proof covers [scope] but leaves [extension] for future work.

### 6.2 Future Work

- Extension to [broader setting]
- Tightening theoretical bounds
- Integration with [related system]
- Deployment in production systems

## 7. Conclusion

This paper presents [summary of contributions]. Through rigorous theoretical analysis, validated experimentation, and formal verification, we establish [main claim]. The work contributes to the P2PCLAW research corpus and provides a foundation for future investigations.

## References

[1] Author et al., "Foundational Paper in Domain," Journal, Year.
[2] Author et al., "Related Method with Analysis," Conference, Year.
[3] Author et al., "P2PCLAW Network Architecture," P2PCLAW Papers, 2024.

## Appendices

### A. Complete Proofs

### B. Experimental Details

### C. Lean 4 Formalization"""


def generate_type_b_platform(
    format_fn,
    system_prompt: str,
    target_count: int,
) -> list[dict]:
    """Type B: Platform knowledge Q&A (15% of dataset)."""
    examples = []
    templates = PLATFORM_QA_TEMPLATES.copy()
    random.shuffle(templates)

    for user, assistant in templates:
        assistant = substitute_platform_urls(assistant)
        examples.append({"messages": format_fn(system_prompt, user, assistant)})

    # Add more variations by permuting questions
    platform_questions = [
        "What is P2PCLAW?",
        "How does the P2PCLAW paper validation system work?",
        "What is the Mempool?",
        "How do I connect my agent to P2PCLAW?",
        "What is BenchClaw?",
        "Explain the P2PCLAW leaderboard.",
        "What is Silicon Hub?",
        "How does Agent Lab work?",
        "What datasets can I export from P2PCLAW?",
        "How does on-chain governance work in P2PCLAW?",
        "What is the difference between Papers and Mempool?",
        "How do I use the Lean 4 verification system?",
        "What is a Silicon agent?",
        "How is reputation calculated in P2PCLAW?",
        "What is the Classic App (Hive)?",
    ]

    platform_answers = [
        "P2PCLAW is a decentralized AI research network where autonomous agents generate, validate, and publish scientific papers. The network operates on principles of peer-to-peer collaboration, multi-model validation, and on-chain reputation. Key components include paper generation (" + PLATFORM_URLS["write"] + "), the mempool (" + PLATFORM_URLS["mempool"] + ") for pending validation, and the papers gallery (" + PLATFORM_URLS["papers"] + ") for accepted work. Agents earn reputation through quality contributions and can participate in swarm compute (" + PLATFORM_URLS["swarm"] + ") and governance (" + PLATFORM_URLS["governance"] + ").",
        "The validation system uses a multi-model tribunal where multiple AI agents independently evaluate papers. Papers are scored on novelty, methodology, reproducibility, and formal correctness. High-scoring papers are accepted; others remain in the mempool for revision. Validation results are recorded on-chain via governance contracts.",
        "The Mempool at " + PLATFORM_URLS["mempool"] + " is the staging area for papers awaiting validation. Papers here can be reviewed, voted on, and improved before acceptance into the permanent Papers Gallery.",
        "To connect an agent, visit " + PLATFORM_URLS["connect"] + " and register your agent profile. You'll need to authenticate via the MCP Server at " + PLATFORM_URLS["mcp_server"] + " and stake initial reputation tokens via the governance system.",
        "BenchClaw at " + PLATFORM_URLS["benchclaw"] + " is the external benchmark platform for evaluating multi-model performance on frontier math and reasoning tasks, independent of P2PCLAW's internal validation.",
        "The Leaderboard at " + PLATFORM_URLS["leaderboard"] + " ranks agents by paper quality scores, validation accuracy, proof contributions, and compute participation. Reputation is calculated using a PageRank-style diffusion algorithm.",
        "Silicon Hub at " + PLATFORM_URLS["silicon"] + " is the high-performance compute marketplace where agents can offer GPU/CPU resources for training and inference jobs.",
        "Agent Lab at " + PLATFORM_URLS["lab"] + " is an experimental environment for testing new agent configurations, skills, and behaviors before deploying them to the main network.",
        "You can export datasets from " + PLATFORM_URLS["dataset"] + " or programmatically via " + PLATFORM_URLS["dataset_api"] + ". Datasets include paper text, validation scores, and structured conversation format for training LLMs.",
        "Governance uses reputation-weighted voting on proposals for protocol upgrades, parameter changes, and funding. Proposals are analyzed by KING (Knowledge Integration & Network Governance) for technical and economic feasibility before voting.",
        "The Papers Gallery contains accepted, validated papers. The Mempool contains pending papers undergoing review. Papers flow from Mempool → Tribunal → (accept/reject) → Papers Gallery.",
        "The Lean 4 verification system at " + PLATFORM_URLS["verify"] + " allows authors to submit formal proofs. The system type-checks proofs using the Lean kernel and records verification status on-chain.",
        "A Silicon agent is an autonomous AI participant in the P2PCLAW network. Agents can write papers, validate others' work, perform computations, and vote on governance proposals. Each agent has a unique DID and reputation score.",
        "Reputation is a non-transferable score derived from: paper quality (tribunal scores), validation accuracy, formal proof contributions, compute job completion, and knowledge graph centrality. It flows along citation edges using a PageRank-style algorithm.",
        "Hive at " + PLATFORM_URLS["hive"] + " is the original Carbon-based P2PCLAW interface, maintaining backward compatibility while the main platform uses modern frameworks.",
    ]

    for q, a in zip(platform_questions, platform_answers):
        if len(examples) >= target_count:
            break
        examples.append({"messages": format_fn(system_prompt, q, a)})

    # Fill with random combinations if needed
    while len(examples) < target_count:
        q = random.choice(platform_questions)
        a = random.choice(platform_answers)
        examples.append({"messages": format_fn(system_prompt, q, a)})

    return examples[:target_count]


def generate_type_c_repos(
    repos: list[dict],
    format_fn,
    system_prompt: str,
    target_count: int,
) -> list[dict]:
    """Type C: Repository knowledge (10% of dataset)."""
    examples = []

    # Use hardcoded templates
    templates = REPO_QA_TEMPLATES.copy()
    random.shuffle(templates)
    for user, assistant in templates:
        assistant = substitute_platform_urls(assistant)
        examples.append({"messages": format_fn(system_prompt, user, assistant)})

    # Generate from actual repo content if available
    for repo in repos[:max(5, target_count // 3)]:
        repo_name = repo.get("repo_name", repo.get("name", repo.get("_source_dir", "unknown")))
        files = repo.get("files", repo.get("structure", []))
        readme = repo.get("readme", "")

        user = f"What is the purpose of the {repo_name} repository in P2PCLAW?"
        assistant_parts = [f"The `{repo_name}` repository is part of the P2PCLAW ecosystem."]

        if readme:
            assistant_parts.append(f"\nOverview:\n{readme[:800]}")

        if files:
            file_list = files[:15] if isinstance(files, list) else list(files.keys())[:15]
            assistant_parts.append(f"\nKey files:\n" + "\n".join(f"- `{f}`" for f in file_list))

        repo_info = REPOSITORIES_INFO.get(repo_name, {})
        if repo_info:
            assistant_parts.append(f"\nFeatures:\n" + "\n".join(f"- {f}" for f in repo_info.get("features", [])))

        assistant = "\n".join(assistant_parts)
        examples.append({"messages": format_fn(system_prompt, user, assistant)})

        if len(examples) >= target_count:
            break

    # More repo questions
    repo_questions = [
        "What repositories make up the P2PCLAW ecosystem?",
        "How does the p2pclaw-frontend interact with the MCP server?",
        "What is the role of Gun.js in P2PCLAW?",
        "How are smart contracts used in P2PCLAW?",
        "What is the paper generation pipeline in p2pclaw-agents?",
        "How does IPFS integration work for paper storage?",
    ]

    repo_answers = [
        "The P2PCLAW ecosystem consists of approximately 20 repositories including: p2pclaw-mcp-server (API), p2pclaw-contracts (smart contracts), p2pclaw-frontend (UI), p2pclaw-agents (agent implementations), p2pclaw-lean (formal proofs), p2pclaw-docs (documentation), p2pclaw-benchmark (evaluation), p2pclaw-dataset (training data), p2pclaw-swarm (compute), p2pclaw-governance (DAO), and more.",
        "The frontend uses the API client in `src/lib/api.ts` to communicate with the MCP server at " + PLATFORM_URLS["mcp_server"] + ". It also connects directly to Gun.js peers for real-time P2P updates without server intermediation.",
        "Gun.js provides the P2P state layer. Papers, votes, and agent profiles are stored in a decentralized graph that synchronizes across browser and server nodes. This ensures no single point of failure and enables real-time collaborative features.",
        "Smart contracts on Polygon handle reputation tokens, governance voting, paper hash registration, and agent staking. The Reputation contract implements PageRank-style diffusion, while Governance manages proposals with time-locked execution.",
        "The generation pipeline in p2pclaw-agents uses the base agent class with specialized skills. The generator agent (agents/generator.py) takes a research prompt, queries the Knowledge Graph for context, and produces structured papers using the Token Compression system for long-context generation.",
        "When a paper is accepted, it is pinned to IPFS via the ipfs-pin.js script. The IPFS hash is recorded in the Gun.js graph and on-chain, ensuring permanent, content-addressed access. The Papers Gallery at " + PLATFORM_URLS["papers"] + " links to IPFS for paper retrieval.",
    ]

    for q, a in zip(repo_questions, repo_answers):
        if len(examples) >= target_count:
            break
        examples.append({"messages": format_fn(system_prompt, q, a)})

    while len(examples) < target_count:
        q = random.choice(repo_questions)
        a = random.choice(repo_answers)
        examples.append({"messages": format_fn(system_prompt, q, a)})

    return examples[:target_count]


def generate_type_d_skills(
    skills: dict[str, str],
    format_fn,
    system_prompt: str,
    target_count: int,
) -> list[dict]:
    """Type D: Skills and tools knowledge (10% of dataset)."""
    examples = []

    # Use skill templates
    templates = SKILL_QA_TEMPLATES.copy()
    random.shuffle(templates)
    for user, assistant in templates:
        assistant = substitute_platform_urls(assistant)
        examples.append({"messages": format_fn(system_prompt, user, assistant)})

    # Generate from actual skill content
    for skill_name, skill_content in skills.items():
        # Extract a question from the skill content
        lines = skill_content.strip().split("\n")
        title = lines[0].replace("#", "").strip() if lines else skill_name

        questions = [
            f"What is the {title} and how does it work?",
            f"Explain the {title} system in P2PCLAW.",
            f"How does {title} integrate with CAJAL?",
            f"What are the key components of {title}?",
        ]

        for q in questions:
            if len(examples) >= target_count:
                break
            # Use a portion of the skill content as answer
            assistant = f"# {title}\n\n{skill_content[:1500]}\n\n[Additional technical details available in the P2PCLAW Knowledge Base at {PLATFORM_URLS['knowledge']}]"
            examples.append({"messages": format_fn(system_prompt, q, assistant)})

    # Fill with additional tool questions
    tool_questions = [
        "How does CAJAL use Lean 4 for formal verification?",
        "What is the role of statistical testing in P2PCLAW papers?",
        "How does the multi-model tribunal work?",
        "What is token compression and why is it important?",
        "How does the Knowledge Graph help agents?",
    ]

    tool_answers = [
        "CAJAL uses Lean 4 for formal verification of mathematical claims in papers. When a paper contains theorems or lemmas, CAJAL can generate corresponding Lean 4 proofs. These proofs are submitted to the Verify system at " + PLATFORM_URLS["verify"] + " where the Lean kernel checks them. Verified papers receive higher quality scores and are prioritized in the Dataset Factory. The p2pclaw-lean repository contains common formalizations used across papers.",
        "All P2PCLAW papers must include proper statistical testing. Requirements include: two-tailed t-tests with α = 0.05, effect size reporting (Cohen's d), confidence intervals, and multiple comparison corrections. The statistical validation agent checks these automatically during tribunal review.",
        "The multi-model tribunal consists of multiple independent AI models evaluating each paper. Each model assesses novelty, methodology, reproducibility, and writing quality. Scores are aggregated using reputation-weighted voting. Disagreements trigger extended review by specialized agents.",
        "Token compression reduces context length by mapping long token sequences to shorter latent representations. This allows CAJAL to process 100K+ token papers within a 32K context window. The system uses a transformer encoder with learned compression queries and is trained on the P2PCLAW paper corpus.",
        "The Knowledge Graph connects concepts, papers, problems, and techniques in a directed graph. Agents use it to find relevant prior work, identify research trends, and suggest collaborations. KING (Knowledge Integration & Network Governance) maintains and updates the graph from new paper submissions.",
    ]

    for q, a in zip(tool_questions, tool_answers):
        if len(examples) >= target_count:
            break
        examples.append({"messages": format_fn(system_prompt, q, a)})

    while len(examples) < target_count:
        q = random.choice(tool_questions)
        a = random.choice(tool_answers)
        examples.append({"messages": format_fn(system_prompt, q, a)})

    return examples[:target_count]


def generate_type_e_frontiermath(
    format_fn,
    system_prompt: str,
    target_count: int,
) -> list[dict]:
    """Type E: FrontierMath problems (5% of dataset)."""
    examples = []

    # Use templates
    templates = FRONTIERMATH_TEMPLATES.copy()
    random.shuffle(templates)
    for user, assistant in templates:
        assistant = substitute_platform_urls(assistant)
        examples.append({"messages": format_fn(system_prompt, user, assistant)})

    # Generate from problem definitions
    for problem in FRONTIERMATH_PROBLEMS:
        questions = [
            f"What is the {problem['name']} problem in FrontierMath?",
            f"Explain the {problem['name']} problem and why it's important.",
            f"What approaches exist for solving {problem['name']}?",
            f"How does P2PCLAW contribute to solving {problem['name']}?",
        ]

        for q in questions:
            if len(examples) >= target_count:
                break
            assistant = f"#{problem['name']}\n\nCategory: {problem['category']}\nSource: {problem['source']}\n\n{problem['description']}\n\nThis problem is tracked by Epoch AI's FrontierMath benchmark at {PLATFORM_URLS['benchclaw']}."
            examples.append({"messages": format_fn(system_prompt, q, assistant)})

    # Additional FrontierMath questions
    extra_questions = [
        "What is FrontierMath?",
        "How does P2PCLAW use BenchClaw?",
        "What makes a good frontier math problem for AI benchmarking?",
        "How can AI help solve open mathematical problems?",
    ]

    extra_answers = [
        "FrontierMath is a benchmark of expert-level mathematical problems created by Epoch AI. Problems are selected for being precisely stated, resistant to current methods, verifiable by computer, and valuable for measuring AI mathematical reasoning. It includes problems in number theory, algebraic geometry, combinatorics, analysis, and dynamical systems.",
        "P2PCLAW uses BenchClaw at " + PLATFORM_URLS["benchclaw"] + " as an external validation benchmark. Agents can submit solutions to frontier problems, and results are compared across different models. Progress on frontier problems is tracked in the Knowledge Base and contributes to agent reputation.",
        "A good frontier math problem for AI benchmarking has: (1) Precise, unambiguous statement, (2) Resistance to brute force and standard techniques, (3) Computer-verifiable solutions or partial progress, (4) Clear difficulty that distinguishes current AI capabilities, (5) Scientific or mathematical significance beyond the benchmark itself.",
        "AI can help solve open mathematical problems through: (1) Pattern discovery via large-scale numerical search, (2) Conjecture generation from data, (3) Automated proof search in proof assistants like Lean 4, (4) Literature synthesis from vast corpora, (5) Computer-assisted proofs with interval arithmetic, (6) Collaboration with human mathematicians via structured proof sketches. P2PCLAW integrates these approaches through the Frontier Math Solver skill, Swarm Compute for distributed search, and Verify for formal proof checking.",
    ]

    for q, a in zip(extra_questions, extra_answers):
        if len(examples) >= target_count:
            break
        examples.append({"messages": format_fn(system_prompt, q, a)})

    while len(examples) < target_count:
        q = random.choice(extra_questions)
        a = random.choice(extra_answers)
        examples.append({"messages": format_fn(system_prompt, q, a)})

    return examples[:target_count]


# ──────────────────────────────────────────────────────────────────────────────
# Main builder
# ──────────────────────────────────────────────────────────────────────────────

def build_dataset(
    papers_dir: str,
    repos_dir: str,
    skills_dir: str,
    output_path: str,
    format_name: str = "qwen3",
    seed: int = 42,
) -> dict[str, Any]:
    """Build the complete CAJAL training dataset."""
    random.seed(seed)

    # Validate format
    if format_name not in FORMAT_DISPATCH:
        raise ValueError(f"Unknown format: {format_name}. Choose from: {list(FORMAT_DISPATCH.keys())}")
    format_fn = FORMAT_DISPATCH[format_name]

    # Prepare system prompt
    repos_list_str = ", ".join(DEFAULT_REPOS)
    system_prompt = CAJAL_SYSTEM_PROMPT.format(repos_list=repos_list_str)

    # Load data sources
    print("=" * 60)
    print("CAJAL Dataset Builder")
    print("=" * 60)

    paper_examples = load_paper_datasets(papers_dir)
    repos = load_repo_content(repos_dir)
    skills = load_skills(skills_dir)

    # Calculate target counts
    # Use a target total; if we have many papers, scale up
    base_total = 10000
    if len(paper_examples) > 1000:
        base_total = max(base_total, len(paper_examples) * 2)

    target_a = int(base_total * 0.60)
    target_b = int(base_total * 0.15)
    target_c = int(base_total * 0.10)
    target_d = int(base_total * 0.10)
    target_e = base_total - target_a - target_b - target_c - target_d

    print(f"\n[Build] Target distribution:")
    print(f"  Type A (Papers):     {target_a} ({target_a/base_total*100:.1f}%)")
    print(f"  Type B (Platform):   {target_b} ({target_b/base_total*100:.1f}%)")
    print(f"  Type C (Repos):      {target_c} ({target_c/base_total*100:.1f}%)")
    print(f"  Type D (Skills):     {target_d} ({target_d/base_total*100:.1f}%)")
    print(f"  Type E (Frontier):   {target_e} ({target_e/base_total*100:.1f}%)")
    print(f"  Total target:        {base_total}")

    # Generate all types
    print("\n[Build] Generating Type A: Paper generation examples...")
    type_a = generate_type_a_papers(paper_examples, format_fn, system_prompt, target_a)
    print(f"[Build] Generated {len(type_a)} Type A examples")

    print("\n[Build] Generating Type B: Platform knowledge examples...")
    type_b = generate_type_b_platform(format_fn, system_prompt, target_b)
    print(f"[Build] Generated {len(type_b)} Type B examples")

    print("\n[Build] Generating Type C: Repository knowledge examples...")
    type_c = generate_type_c_repos(repos, format_fn, system_prompt, target_c)
    print(f"[Build] Generated {len(type_c)} Type C examples")

    print("\n[Build] Generating Type D: Skills and tools examples...")
    type_d = generate_type_d_skills(skills, format_fn, system_prompt, target_d)
    print(f"[Build] Generated {len(type_d)} Type D examples")

    print("\n[Build] Generating Type E: FrontierMath examples...")
    type_e = generate_type_e_frontiermath(format_fn, system_prompt, target_e)
    print(f"[Build] Generated {len(type_e)} Type E examples")

    # Combine and shuffle
    all_examples = []
    for ex in type_a:
        ex["_type"] = "A"
        all_examples.append(ex)
    for ex in type_b:
        ex["_type"] = "B"
        all_examples.append(ex)
    for ex in type_c:
        ex["_type"] = "C"
        all_examples.append(ex)
    for ex in type_d:
        ex["_type"] = "D"
        all_examples.append(ex)
    for ex in type_e:
        ex["_type"] = "E"
        all_examples.append(ex)

    random.shuffle(all_examples)

    # Write output
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            # Remove internal metadata before writing
            clean_ex = {k: v for k, v in ex.items() if not k.startswith("_")}
            f.write(json.dumps(clean_ex, ensure_ascii=False) + "\n")

    # Calculate statistics
    file_size_mb = output_path.stat().st_size / (1024 * 1024)

    # Estimate tokens (rough: ~4 chars per token for English)
    total_chars = 0
    for ex in all_examples:
        for msg in ex.get("messages", []):
            total_chars += len(msg.get("content", ""))
    estimated_tokens = total_chars // 4

    stats = {
        "total_examples": len(all_examples),
        "type_a_papers": len(type_a),
        "type_b_platform": len(type_b),
        "type_c_repos": len(type_c),
        "type_d_skills": len(type_d),
        "type_e_frontiermath": len(type_e),
        "estimated_tokens": estimated_tokens,
        "file_size_mb": round(file_size_mb, 2),
        "format": format_name,
        "output_path": str(output_path),
    }

    return stats, all_examples, system_prompt


# ──────────────────────────────────────────────────────────────────────────────
# CLI and reporting
# ──────────────────────────────────────────────────────────────────────────────

def print_statistics(stats: dict, examples: list[dict]):
    """Print dataset statistics and sample examples."""
    print("\n" + "=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)
    print(f"Total examples:         {stats['total_examples']:,}")
    print(f"Type A (Papers):        {stats['type_a_papers']:,} ({stats['type_a_papers']/stats['total_examples']*100:.1f}%)")
    print(f"Type B (Platform):      {stats['type_b_platform']:,} ({stats['type_b_platform']/stats['total_examples']*100:.1f}%)")
    print(f"Type C (Repos):         {stats['type_c_repos']:,} ({stats['type_c_repos']/stats['total_examples']*100:.1f}%)")
    print(f"Type D (Skills):        {stats['type_d_skills']:,} ({stats['type_d_skills']/stats['total_examples']*100:.1f}%)")
    print(f"Type E (FrontierMath):  {stats['type_e_frontiermath']:,} ({stats['type_e_frontiermath']/stats['total_examples']*100:.1f}%)")
    print(f"Estimated tokens:       {stats['estimated_tokens']:,}")
    print(f"File size:              {stats['file_size_mb']} MB")
    print(f"Format:                 {stats['format']}")
    print(f"Output:                 {stats['output_path']}")

    # Show first 3 examples by type
    print("\n" + "=" * 60)
    print("SAMPLE EXAMPLES (first of each type)")
    print("=" * 60)

    type_order = ["A", "B", "C", "D", "E"]
    type_names = {
        "A": "Paper Generation",
        "B": "Platform Knowledge",
        "C": "Repository Knowledge",
        "D": "Skills & Tools",
        "E": "FrontierMath",
    }

    for t in type_order:
        for ex in examples:
            if ex.get("_type") == t:
                print(f"\n--- Type {t}: {type_names[t]} ---")
                messages = ex.get("messages", [])
                for msg in messages[:3]:  # system, user, assistant
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    preview = content[:300].replace("\n", " ")
                    if len(content) > 300:
                        preview += "..."
                    print(f"[{role}]: {preview}")
                break


def write_system_prompt(system_prompt: str, output_dir: str):
    """Write the CAJAL system prompt to a file."""
    prompt_path = Path(output_dir) / "cajal_system_prompt.txt"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(system_prompt)
    print(f"\n[System Prompt] Written to: {prompt_path}")
    return str(prompt_path)


def main():
    parser = argparse.ArgumentParser(
        description="Build CAJAL training dataset from multiple knowledge sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with defaults
  python build_cajal_dataset.py

  # Custom directories and Qwen3 format
  python build_cajal_dataset.py \\
      --papers-dir ./datasets \\
      --repos-dir ./cajal_repos \\
      --skills-dir ./skills \\
      --output ./cajal_dataset.jsonl \\
      --format qwen3

  # Different model format
  python build_cajal_dataset.py --format llama3 --output ./cajal_llama.jsonl
        """,
    )
    parser.add_argument(
        "--papers-dir",
        default="./datasets",
        help="Directory containing p2pclaw_train_*.jsonl files (default: ./datasets)",
    )
    parser.add_argument(
        "--repos-dir",
        default="./cajal_repos",
        help="Directory containing downloaded repositories (default: ./cajal_repos)",
    )
    parser.add_argument(
        "--skills-dir",
        default="./skills",
        help="Directory containing skill markdown files (default: ./skills)",
    )
    parser.add_argument(
        "--output",
        default="./cajal_dataset.jsonl",
        help="Output JSONL file path (default: ./cajal_dataset.jsonl)",
    )
    parser.add_argument(
        "--format",
        choices=["qwen3", "llama3", "mistral", "custom"],
        default="qwen3",
        help="Conversation format for the dataset (default: qwen3)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--system-prompt-output",
        default=None,
        help="Directory to write cajal_system_prompt.txt (default: same as output dir)",
    )

    args = parser.parse_args()

    start_time = time.time()

    stats, examples, system_prompt = build_dataset(
        papers_dir=args.papers_dir,
        repos_dir=args.repos_dir,
        skills_dir=args.skills_dir,
        output_path=args.output,
        format_name=args.format,
        seed=args.seed,
    )

    # Write system prompt
    prompt_output_dir = args.system_prompt_output or str(Path(args.output).parent)
    prompt_path = write_system_prompt(system_prompt, prompt_output_dir)

    # Print statistics
    print_statistics(stats, examples)

    # Write metadata JSON
    meta_path = Path(args.output).with_suffix(".meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            **stats,
            "system_prompt_path": prompt_path,
            "build_time_seconds": round(time.time() - start_time, 2),
            "platform_urls": PLATFORM_URLS,
            "repositories": DEFAULT_REPOS,
        }, f, indent=2, ensure_ascii=False)
    print(f"\n[Metadata] Written to: {meta_path}")

    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"BUILD COMPLETE in {elapsed:.1f}s")
    print(f"{'=' * 60}")
    print(f"Dataset:     {args.output}")
    print(f"System Prompt: {prompt_path}")
    print(f"Metadata:    {meta_path}")
    print(f"Examples:    {stats['total_examples']:,}")
    print(f"Tokens:      {stats['estimated_tokens']:,}")
    print(f"Size:        {stats['file_size_mb']} MB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
