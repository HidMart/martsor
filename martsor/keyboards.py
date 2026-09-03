class Button:
    """
    Martsor inline/glass button.

    The button is converted to the native SPlusthon
    button object when used with SelfClient.
    """

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

    @classmethod
    def inline(cls, text, data=None, callback_data=None):
        """
        Create an inline/glass callback button.

        Example:
            Button.inline("Click me", data="hello")
        """

        if callback_data is not None:
            data = callback_data

        return cls(
            text=text,
            callback_data=data,
        )

    @classmethod
    def callback(cls, text, data=None):
        """
        Alias for Button.inline().
        """

        return cls.inline(
            text,
            data=data,
        )

    @classmethod
    def url(cls, text, url):
        """
        Create an URL button.
        """

        return cls(
            text=text,
            url=url,
        )

    def to_dict(self):
        """
        Convert the button to a dictionary.
        """

        data = {
            "text": self.text,
        }

        if self.callback_data is not None:
            data["callback_data"] = self.callback_data

        if self.url is not None:
            data["url"] = self.url

        if self.switch_inline_query is not None:
            data["switch_inline_query"] = (
                self.switch_inline_query
            )

        if self.switch_inline_query_current_chat is not None:
            data["switch_inline_query_current_chat"] = (
                self.switch_inline_query_current_chat
            )

        return data

    def __repr__(self):
        return (
            f"Button("
            f"text={self.text!r}, "
            f"callback_data={self.callback_data!r}, "
            f"url={self.url!r}"
            f")"
        )


class InlineKeyboard:
    """
    Inline / glass keyboard.
    """

    def __init__(self, rows=None):
        self.rows = rows or []

    @staticmethod
    def button(
        text,
        callback_data=None,
        data=None,
    ):
        if data is not None:
            callback_data = data

        return Button.inline(
            text,
            callback_data=callback_data,
        )

    @staticmethod
    def callback(
        text,
        data=None,
    ):
        return Button.inline(
            text,
            data=data,
        )

    @staticmethod
    def url(text, url):
        return Button.url(
            text,
            url,
        )

    def add_row(self, *buttons):
        self.rows.append(list(buttons))
        return self

    def add(self, *buttons):
        return self.add_row(*buttons)

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
                        "Keyboard buttons must be "
                        "Button or dict."
                    )

            result.append(converted_row)

        return {
            "inline_keyboard": result
        }

    def __iter__(self):
        return iter(self.rows)

    def __repr__(self):
        return (
            f"InlineKeyboard(rows={self.rows!r})"
        )


class ReplyKeyboard:
    """
    Reply keyboard.
    """

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
    """
    Remove reply keyboard.
    """

    def __init__(self, selective=False):
        self.selective = selective

    def to_dict(self):
        return {
            "remove_keyboard": True,
            "selective": self.selective,
        }


class ForceReply:
    """
    Force a reply from the user.
    """

    def __init__(self, selective=False):
        self.selective = selective

    def to_dict(self):
        return {
            "force_reply": True,
            "selective": self.selective,
        }