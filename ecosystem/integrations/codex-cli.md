# CAJAL + Codex CLI Integration

> Codex CLI is OpenAI's official coding agent for the terminal.

## Setup

### 1. Install Codex CLI

```bash
npm install -g @openai/codex
```

### 2. Configure for CAJAL (Local Mode)

Codex CLI supports custom providers via the OpenAI-compatible API:

```bash
# Set CAJAL as the backend
export OPENAI_BASE_URL=http://localhost:8765/v1
export OPENAI_API_KEY=sk-cajal-local

# Run Codex with CAJAL
codex --model cajal-4b
```

### 3. Using CAJAL with Codex

```bash
# Interactive mode
codex --model cajal-4b

# Single command
codex --model cajal-4b "Review this smart contract for vulnerabilities"

# With file context
codex --model cajal-4b -f contract.sol "Audit this contract"

# Approval mode (recommended for CAJAL's rigorous analysis)
codex --model cajal-4b --approval
```

### 4. CAJAL System Prompt for Codex

Create `~/.codex/instructions.md`:

```markdown
You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich, Switzerland.

When writing or reviewing code:
1. Prioritize security and correctness over convenience
2. Consider decentralization implications
3. Use formal verification where applicable
4. Document cryptographic assumptions
5. Analyze game-theoretic incentives
```

## Features

| Feature | Command |
|---------|---------|
| Code generation | `codex "implement X"` |
| Code review | `codex -f file.rs "review this"` |
| Refactoring | `codex -f src/ "refactor for P2P"` |
| Testing | `codex "write tests for X"` |

## Tips

- Use `--approval` mode to review CAJAL's changes before applying
- CAJAL is conservative — it may suggest more robust but verbose solutions
- Combine with `git diff` to review all changes
