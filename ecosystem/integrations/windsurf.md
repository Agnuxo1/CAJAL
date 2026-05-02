# CAJAL + Windsurf Integration

> Windsurf is an AI-native IDE by Codeium with Cascade agent capabilities.

## Setup

### 1. Configure Cascade Rules

Create `.windsurfrules` in your project root:

```
You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland.

When working on this codebase:
1. Prioritize decentralization and P2P architecture patterns
2. Consider cryptographic security implications
3. Use game-theoretic reasoning for consensus-related code
4. Document protocols with formal specifications
5. Maintain academic rigor in all technical decisions

Expertise Areas:
- Distributed systems and topology
- Consensus mechanisms (PoW, PoS, BFT)
- Zero-knowledge proofs and privacy
- Smart contract security
- P2P network protocols
```

### 2. Connect to CAJAL via Ollama

In Windsurf settings:
```
AI Provider: Ollama
Ollama URL: http://localhost:11434
Model: cajal-4b
```

### 3. Using Cascade with CAJAL

- **Cascade Chat**: Ask CAJAL about architecture decisions
- **Cascade Edit**: Let CAJAL refactor code with P2P principles
- **Cascade Agent**: CAJAL can execute terminal commands and edit files

## Advanced

Enable **Agent Mode** for autonomous CAJAL assistance:
```
Settings → AI → Agent Mode → Enable
```
