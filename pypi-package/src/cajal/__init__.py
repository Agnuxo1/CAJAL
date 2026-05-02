"""
CAJAL-4B CLI - The complete command-line interface for the CAJAL scientific intelligence model.

Named in honor of Santiago Ramon y Cajal, the father of modern neuroscience.
CAJAL is a specialized LLM for peer-to-peer systems, cryptography, and scientific research.

Quick start:
    >>> import cajal
    >>> client = cajal.CajalClient()
    >>> response = client.chat("Explain P2PCLAW governance")
"""

__version__ = "1.0.0"
__author__ = "P2PCLAW Lab"
__license__ = "MIT"

from .client import CajalClient
from .config import get_config, save_config, DEFAULT_CONFIG

__all__ = [
    "CajalClient",
    "get_config",
    "save_config",
    "DEFAULT_CONFIG",
    "__version__",
]
