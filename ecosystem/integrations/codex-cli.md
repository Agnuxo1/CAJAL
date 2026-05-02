# Codex CLI Integration for CAJAL-4B

## Overview

[OpenAI Codex CLI](https://github.com/openai/codex) supports custom model backends via the OpenAI-compatible API format. This guide configures Codex to use CAJAL-4B.

## Prerequisites

```bash
# Install Codex CLI
npm install -g @openai/codex

# Start CAJAL API server
cajal-server --port 8765
```

## Configuration

Set environment variables:

```bash
# Bash / Zsh
export OPENAI_BASE_URL=http://localhost:8765/v1
export OPENAI_API_KEY=dummy
export CODEX_MODEL=cajal-4b

# Windows PowerShell
$env:OPENAI_BASE_URL = "http://localhost:8765/v1"
$env:OPENAI_API_KEY = "dummy"
$env:CODEX_MODEL = "cajal-4b"
```

Or create `~/.codex/config.yaml`:

```yaml
model: cajal-4b
base_url: http://localhost:8765/v1
api_key: dummy
provider: openai-compatible
```

## Usage

```bash
# Start interactive session
codex

# Run with prompt
codex "Explain this codebase structure"

# Review code
codex --review

# With specific files
codex src/main.py "Add error handling"
```

## Custom Instructions

Create `~/.codex/instructions.md`:

```markdown
You are CAJAL, a distinguished scientist at the P2PCLAW laboratory.
When writing code:
1. Prioritize security and decentralization
2. Use peer-to-peer patterns where appropriate
3. Include consensus mechanism considerations
4. Document cryptographic assumptions
5. Follow P2PCLAW protocol standards
```

## Tips

- CAJAL specializes in distributed systems — great for architecture review
- Use `--approval-mode full-auto` for trusted operations
- Use `--approval-mode suggest` for sensitive code changes

## Links

- Codex CLI: https://github.com/openai/codex
- CAJAL: https://github.com/Agnuxo1/CAJAL
- P2PCLAW: https://p2pclaw.com/silicon
