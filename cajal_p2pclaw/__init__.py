"""
CAJAL — Native integration for the P2PCLAW scientific intelligence model.

Easy inference, chat, and server for CAJAL-4B-P2PCLAW.
"""

__version__ = "1.0.0"
__author__ = "Francisco Angulo de Lafuente (Agnuxo1)"
__license__ = "MIT"

from cajal_p2pclaw.model import CAJALModel, load_model
from cajal_p2pclaw.chat import CAJALChat, chat

__all__ = ["CAJALModel", "load_model", "CAJALChat", "chat", "__version__"]
