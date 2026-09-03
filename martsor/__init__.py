"""
Martsor
=======

Async Python library for Soroush Plus bots and user clients.
"""

from .client import Client, Bot

from .errors import (
    MartsorError,
    APIError,
    AuthenticationError,
    AuthorizationError,
)

from .keyboards import (
    Button,
    InlineKeyboard,
    ReplyKeyboard,
    ReplyKeyboardRemove,
    ForceReply,
)

try:
    from .types import (
        User,
        Chat,
        Message,
    )
except ImportError:
    User = None
    Chat = None
    Message = None

try:
    from .self_client import SelfClient
except ImportError:
    SelfClient = None


__version__ = "0.3.1"


__all__ = [
    "Client",
    "Bot",
    "SelfClient",

    "MartsorError",
    "APIError",
    "AuthenticationError",
    "AuthorizationError",

    "Button",
    "InlineKeyboard",
    "ReplyKeyboard",
    "ReplyKeyboardRemove",
    "ForceReply",

    "User",
    "Chat",
    "Message",

    "__version__",
]