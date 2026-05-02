"""
CAJAL Python Package
P2PCLAW-optimized LLM — honoring Santiago Ramón y Cajal

Official package for CAJAL-4B, available on:
- PyPI: pip install cajal
- GitHub: https://github.com/Agnuxo1/CAJAL
- HuggingFace: https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW
"""

__version__ = "1.0.0"
__author__ = "P2PCLAW Research"
__license__ = "MIT"

from .core import CAJAL
from .config import get_config, save_config

__all__ = ["CAJAL", "get_config", "save_config", "__version__"]
