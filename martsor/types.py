from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class User:
    id: Optional[int] = None
    is_bot: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return None

        return cls(
            id=data.get("id"),
            is_bot=data.get("is_bot"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            username=data.get("username"),
        )


@dataclass
class Chat:
    id: Optional[Any] = None
    type: Optional[str] = None
    title: Optional[str] = None
    username: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return None

        return cls(
            id=data.get("id"),
            type=data.get("type"),
            title=data.get("title"),
            username=data.get("username"),
        )


@dataclass
class Message:
    message_id: Optional[Any] = None
    from_user: Optional[User] = None
    date: Optional[Any] = None
    chat: Optional[Chat] = None
    text: Optional[str] = None
    caption: Optional[str] = None
    photo: Any = None
    video: Any = None
    audio: Any = None
    document: Any = None
    reply_to_message: Any = None
    raw: Optional[Dict[str, Any]] = None

    @property
    def chat_id(self):
        if self.chat:
            return self.chat.id
        return None

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return None

        return cls(
            message_id=data.get("message_id"),
            from_user=User.from_dict(data.get("from")),
            date=data.get("date"),
            chat=Chat.from_dict(data.get("chat")),
            text=data.get("text"),
            caption=data.get("caption"),
            photo=data.get("photo"),
            video=data.get("video"),
            audio=data.get("audio"),
            document=data.get("document"),
            reply_to_message=data.get("reply_to_message"),
            raw=data,
        )


@dataclass
class CallbackQuery:
    id: Optional[str] = None
    from_user: Optional[User] = None
    data: Optional[str] = None
    message: Optional[Message] = None
    raw: Optional[Dict[str, Any]] = None

    @property
    def chat_id(self):
        if self.message:
            return self.message.chat_id
        return None

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return None

        return cls(
            id=data.get("id"),
            from_user=User.from_dict(data.get("from")),
            data=data.get("data"),
            message=Message.from_dict(data.get("message")),
            raw=data,
        )


@dataclass
class Update:
    update_id: Optional[int] = None
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    raw: Optional[Dict[str, Any]] = None

    @property
    def text(self):
        if self.message:
            return self.message.text

        if self.edited_message:
            return self.edited_message.text

        return None

    @property
    def chat_id(self):
        if self.message:
            return self.message.chat_id

        if self.edited_message:
            return self.edited_message.chat_id

        if self.callback_query:
            return self.callback_query.chat_id

        return None

    @property
    def message_id(self):
        if self.message:
            return self.message.message_id

        if self.edited_message:
            return self.edited_message.message_id

        if self.callback_query and self.callback_query.message:
            return self.callback_query.message.message_id

        return None

    @property
    def data(self):
        if self.callback_query:
            return self.callback_query.data

        return None

    @property
    def callback_query_id(self):
        if self.callback_query:
            return self.callback_query.id

        return None

    def answer(self, text=None, show_alert=False):
        return None

    @classmethod
    def from_dict(cls, data):
        return cls(
            update_id=data.get("update_id"),
            message=Message.from_dict(data.get("message")),
            edited_message=Message.from_dict(
                data.get("edited_message")
            ),
            callback_query=CallbackQuery.from_dict(
                data.get("callback_query")
            ),
            raw=data,
        )