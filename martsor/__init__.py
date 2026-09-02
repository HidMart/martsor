"""
martsor - Python library for building Soroush Plus bots.
"""

from .client import Bot, Client

from .errors import (
    APIError,
    MartsorError,
)

from .keyboards import (
    Button,
    ForceReply,
    InlineKeyboard,
    ReplyKeyboard,
    ReplyKeyboardRemove,
)

from .types import (
    CallbackQuery,
    Chat,
    Message,
    Update,
    User,
)


__version__ = "0.3.0"


# =========================================================
# Self Client
# =========================================================

try:
    from .self_client import SelfClient
except ImportError:
    SelfClient = None


__all__ = [
    # Bot
    "Bot",
    "Client",

    # Self Client
    "SelfClient",

    # Keyboards
    "Button",
    "InlineKeyboard",
    "ReplyKeyboard",
    "ReplyKeyboardRemove",
    "ForceReply",

    # Types
    "User",
    "Chat",
    "Message",
    "CallbackQuery",
    "Update",

    # Errors
    "MartsorError",
    "APIError",

    # Version
    "__version__",
]