"""
Martsor
Async Python framework for Soroush Plus.

Version: 0.3.1
"""

from .client import Bot, Client
from .errors import (
    MartsorError,
    APIError,
    AuthenticationError,
    HandlerError,
)
from .keyboards import (
    Button,
    InlineKeyboard,
    ReplyKeyboard,
    ReplyKeyboardRemove,
    ForceReply,
)
from .types import (
    User,
    Chat,
    Message,
    Update,
)

__version__ = "0.3.1"

try:
    from .self_client import SelfClient
except ImportError:
    SelfClient = None


__all__ = [
    "Bot",
    "Client",
    "SelfClient",

    "Button",
    "InlineKeyboard",
    "ReplyKeyboard",
    "ReplyKeyboardRemove",
    "ForceReply",

    "User",
    "Chat",
    "Message",
    "Update",

    "MartsorError",
    "APIError",
    "AuthenticationError",
    "HandlerError",

    "__version__",
]