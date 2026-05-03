# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in CAJAL, please report it responsibly:

1. **Do NOT** open a public issue
2. Email: contact@p2pclaw.com
3. Subject: `[SECURITY] CAJAL — Brief description`
4. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Response Timeline

| Phase | Timeline |
|-------|----------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 7 days |
| Fix + release | Within 30 days (critical), 90 days (non-critical) |
| Public disclosure | After fix is released + 30 days |

## Security Considerations

### Local Execution
CAJAL runs entirely locally. No data leaves your machine unless you explicitly:
- Push to GitHub
- Upload to HuggingFace
- Share via email

### API Keys
If using CAJAL with external services (arXiv, CrossRef):
- Keys are stored in `~/.cajal/config.yaml`
- File permissions should be `600`
- Never commit API keys to version control

### Model Downloads
Models are downloaded from HuggingFace/Ollama registries:
- Verify checksums when available
- Use trusted sources only

## Acknowledgments

Security researchers who have responsibly disclosed vulnerabilities will be acknowledged in release notes and SECURITY.md.

---

**Sponsor this project:** [github.com/sponsors/Agnuxo1](https://github.com/sponsors/Agnuxo1)
