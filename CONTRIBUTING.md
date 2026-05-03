# Contributing to CAJAL

Thank you for your interest in CAJAL! This document provides guidelines for contributing.

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists
2. Use the [bug report template](../../issues/new?template=bug_report.md)
3. Include reproduction steps, environment details, and logs

### Requesting Integrations

1. Check if the platform is already listed in [INTEGRATIONS_HUB.md](INTEGRATIONS_HUB.md)
2. Use the [integration request template](../../issues/new?template=integration_request.md)
3. Provide documentation links and proposed API

### Submitting Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add tests if applicable
5. Commit with clear messages
6. Push and open a Pull Request

## Development Setup

```bash
# Clone
git clone https://github.com/Agnuxo1/CAJAL.git
cd CAJAL

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .
```

## Code Style

- Python: PEP 8, max line length 88 (Black)
- JavaScript/TypeScript: Prettier
- Commit messages: Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)

## Areas Needing Help

| Priority | Area | Skills Needed |
|----------|------|---------------|
| 🔴 High | LaTeX output engine | Python, LaTeX |
| 🔴 High | Zotero integration | Python, REST APIs |
| 🟡 Medium | Multi-language support | i18n, NLP |
| 🟡 Medium | LangChain wrapper | Python, LangChain |
| 🟢 Low | Additional IDE plugins | TypeScript, VS Code API |

## Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Invited to project Discord (coming soon)

## Questions?

- Open a [discussion](../../discussions)
- Email: contact@p2pclaw.com

---

**Sponsor this project:** [github.com/sponsors/Agnuxo1](https://github.com/sponsors/Agnuxo1)
