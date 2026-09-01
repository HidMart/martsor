class Button:
    """Represents an inline keyboard button."""

    def __init__(
        self,
        text,
        callback_data=None,
        url=None,
        switch_inline_query=None,
        switch_inline_query_current_chat=None,
    ):
        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = (
            switch_inline_query_current_chat
        )

    def to_dict(self):
        data = {
            "text": self.text,
        }

        if self.callback_data is not None:
            data["callback_data"] = self.callback_data

        if self.url is not None:
            data["url"] = self.url

        if self.switch_inline_query is not None:
            data["switch_inline_query"] = self.switch_inline_query

        if self.switch_inline_query_current_chat is not None:
            data["switch_inline_query_current_chat"] = (
                self.switch_inline_query_current_chat
            )

        return data


class InlineKeyboard:
    """Inline / glass keyboard."""

    def __init__(self, rows=None):
        self.rows = rows or []

    @staticmethod
    def button(text, callback_data=None):
        return Button(
            text=text,
            callback_data=callback_data,
        )

    @staticmethod
    def url(text, url):
        return Button(
            text=text,
            url=url,
        )

    def add_row(self, *buttons):
        self.rows.append(list(buttons))
        return self

    def to_dict(self):
        result = []

        for row in self.rows:
            converted_row = []

            for button in row:
                if isinstance(button, Button):
                    converted_row.append(button.to_dict())
                elif isinstance(button, dict):
                    converted_row.append(button)
                else:
                    raise TypeError(
                        "Keyboard buttons must be Button or dict."
                    )

            result.append(converted_row)

        return {
            "inline_keyboard": result
        }


class ReplyKeyboard:
    """Reply keyboard."""

    def __init__(
        self,
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=False,
    ):
        self.keyboard = keyboard
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective

    def to_dict(self):
        return {
            "keyboard": self.keyboard,
            "resize_keyboard": self.resize_keyboard,
            "one_time_keyboard": self.one_time_keyboard,
            "selective": self.selective,
        }


class ReplyKeyboardRemove:
    """Remove reply keyboard."""

    def __init__(self, selective=False):
        self.selective = selective

    def to_dict(self):
        return {
            "remove_keyboard": True,
            "selective": self.selective,
        }


class ForceReply:
    """Force a reply from the user."""

    def __init__(self, selective=False):
        self.selective = selective

    def to_dict(self):
        return {
            "force_reply": True,
            "selective": self.selective,
        }