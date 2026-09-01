from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Message:
    """Represents a message received by the bot."""

    chat_id: Optional[str] = None
    text: Optional[str] = None
    message_id: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


@dataclass
class Update:
    """Represents an incoming bot update."""

    update_id: Optional[str] = None
    message: Optional[Message] = None
    raw: Optional[Dict[str, Any]] = None