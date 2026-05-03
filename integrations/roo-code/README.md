# CAJAL + Roo Code Integration

This directory contains the `.roomodes` custom mode file for integrating CAJAL as a Roo Code marketplace custom mode.

## Installation

1. Copy `.roomodes` to your project root or import via Roo Code marketplace
2. Select "CAJAL Scientific Paper Generator" from the mode dropdown
3. Start generating papers with verified arXiv citations

## Features

- 7-section paper generation (IMRAD + Abstract/Conclusion)
- Real arXiv citation verification
- Tribunal scoring with 3 simulated reviewers
- BibTeX export

## Requirements

- CAJAL model running via Ollama: `ollama run cajal-p2pclaw`
- Roo Code with Ollama provider configured
