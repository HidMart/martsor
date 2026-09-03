"""
Martsor Self Client.

User account client for Soroush Plus.
Version: 0.3.1
"""

import inspect
import re

from .keyboards import Button, InlineKeyboard


class SelfClient:
    """
    Client for Soroush Plus user accounts.

    SPlusthon is managed automatically by Martsor.
    """

    def __init__(
        self,
        session=None,
        api_id=None,
        api_hash=None,
        **kwargs
    ):
        try:
            from splusthon import SoroushClient, events
            from splusthon.sessions import StringSession
        except ImportError as exc:
            raise ImportError(
                "Martsor SelfClient backend is not available. "
                "Please reinstall Martsor with its dependencies."
            ) from exc

        self._events = events
        self._StringSession = StringSession
        self._SoroushClient = SoroushClient

        if session is None:
            session = StringSession()
        elif isinstance(session, str):
            session = StringSession(session)

        options = dict(kwargs)

        if api_id is not None:
            options["api_id"] = api_id

        if api_hash is not None:
            options["api_hash"] = api_hash

        self.client = SoroushClient(
            session,
            **options
        )

        self._message_handlers = []
        self._command_handlers = []
        self._callback_handlers = []

        self._events_installed = False
        self._started = False

    # ============================================================
    # Internal helpers
    # ============================================================

    async def _call(self, function, *args, **kwargs):
        result = function(*args, **kwargs)

        if inspect.isawaitable(result):
            return await result

        return result

    async def _call_method(self, name, *args, **kwargs):
        method = getattr(self.client, name, None)

        if method is None:
            raise AttributeError(
                "Martsor backend does not provide method: " + name
            )

        return await self._call(
            method,
            *args,
            **kwargs
        )

    # ============================================================
    # Keyboard support
    # ============================================================

    @staticmethod
    def _convert_button(button):
        """
        Convert a Martsor button into a SPlusthon button.
        """

        try:
            from splusthon import Button as SPlusButton
        except ImportError as exc:
            raise ImportError(
                "SPlusthon is required for SelfClient buttons."
            ) from exc

        # Already a native SPlusthon button
        if isinstance(button, SPlusButton):
            return button

        # Martsor Button
        if isinstance(button, Button):
            if button.url is not None:
                return SPlusButton.url(
                    button.text,
                    button.url
                )

            callback_data = (
                button.callback_data
                if button.callback_data is not None
                else button.switch_inline_query
            )

            if callback_data is not None:
                return SPlusButton.inline(
                    button.text,
                    data=callback_data
                )

            return SPlusButton.inline(
                button.text,
                data=button.text
            )

        # Dictionary support
        if isinstance(button, dict):
            text = button.get("text", "")

            if button.get("url") is not None:
                return SPlusButton.url(
                    text,
                    button["url"]
                )

            data = button.get(
                "callback_data",
                button.get("data")
            )

            if data is not None:
                return SPlusButton.inline(
                    text,
                    data=data
                )

        # Unknown button type
        return button

    @classmethod
    def _convert_buttons(cls, buttons):
        """
        Convert Martsor keyboard definitions to SPlusthon format.
        """

        if buttons is None:
            return None

        # Martsor InlineKeyboard
        if isinstance(buttons, InlineKeyboard):
            buttons = buttons.rows

        # Single button
        if isinstance(buttons, Button):
            return cls._convert_button(buttons)

        # Single dictionary button
        if isinstance(buttons, dict):
            return cls._convert_button(buttons)

        # Nested keyboard rows
        if isinstance(buttons, (list, tuple)):
            result = []

            for item in buttons:
                if isinstance(item, (list, tuple)):
                    row = []

                    for button in item:
                        row.append(
                            cls._convert_button(button)
                        )

                    result.append(row)

                else:
                    result.append(
                        cls._convert_button(item)
                    )

            return result

        return buttons

    # ============================================================
    # Report helpers
    # ============================================================

    @staticmethod
    def _get_report_reason(reason):
        from splusthon.tl.types import (
            InputReportReasonChildAbuse,
            InputReportReasonCopyright,
            InputReportReasonFake,
            InputReportReasonGeoIrrelevant,
            InputReportReasonIllegalDrugs,
            InputReportReasonOther,
            InputReportReasonPersonalDetails,
            InputReportReasonPornography,
            InputReportReasonSpam,
            InputReportReasonViolence,
        )

        reasons = {
            "spam": InputReportReasonSpam,
            "fake": InputReportReasonFake,
            "violence": InputReportReasonViolence,
            "pornography": InputReportReasonPornography,
            "child_abuse": InputReportReasonChildAbuse,
            "copyright": InputReportReasonCopyright,
            "geo_irrelevant": InputReportReasonGeoIrrelevant,
            "illegal_drugs": InputReportReasonIllegalDrugs,
            "other": InputReportReasonOther,
            "personal_details": InputReportReasonPersonalDetails,
        }

        if not isinstance(reason, str):
            raise TypeError(
                "reason must be a string"
            )

        key = (
            reason
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        reason_class = reasons.get(key)

        if reason_class is None:
            available = ", ".join(reasons.keys())

            raise ValueError(
                f"Unknown report reason: {reason}. "
                f"Available reasons: {available}"
            )

        return reason_class()

    async def report_message(
        self,
        entity,
        message_id,
        reason="spam",
        message=""
    ):
        from splusthon.tl.functions.messages import ReportRequest

        if (
            isinstance(message_id, bool)
            or not isinstance(message_id, int)
            or message_id <= 0
        ):
            raise ValueError(
                "message_id must be a positive integer"
            )

        peer = await self.get_input_entity(entity)

        request = ReportRequest(
            peer=peer,
            id=[message_id],
            reason=self._get_report_reason(reason),
            message=message or "",
        )

        return await self._call(
            self.client,
            request
        )

    async def report_peer(
        self,
        entity,
        reason="spam",
        message=""
    ):
        from splusthon.tl.functions.account import ReportPeerRequest

        peer = await self.get_input_entity(entity)

        request = ReportPeerRequest(
            peer=peer,
            reason=self._get_report_reason(reason),
            message=message or "",
        )

        return await self._call(
            self.client,
            request
        )

    async def report_spam(self, entity):
        from splusthon.tl.functions.messages import ReportSpamRequest

        peer = await self.get_input_entity(entity)

        request = ReportSpamRequest(
            peer=peer
        )

        return await self._call(
            self.client,
            request
        )

    # ============================================================
    # Session
    # ============================================================

    @property
    def session(self):
        return self.client.session

    # ============================================================
    # Handlers
    # ============================================================

    def on_message(self, function=None):

        def decorator(handler):
            self._message_handlers.append(handler)
            return handler

        if function is not None:
            return decorator(function)

        return decorator

    def on_command(self, command):
        command = command.lstrip("/").lower()

        def decorator(handler):
            self._command_handlers.append(
                (command, handler)
            )
            return handler

        return decorator

    def on_callback(self, function=None):

        def decorator(handler):
            self._callback_handlers.append(handler)
            return handler

        if function is not None:
            return decorator(function)

        return decorator

    async def _run_handler(self, handler, event):
        result = handler(event)

        if inspect.isawaitable(result):
            return await result

        return result

    async def _dispatch_message(self, event):
        text = getattr(
            event,
            "text",
            None
        )

        if text is None:
            text = ""

        for handler in self._message_handlers:
            try:
                await self._run_handler(
                    handler,
                    event
                )
            except Exception as exc:
                print(
                    "[martsor] Message handler error:",
                    exc
                )

        if text.startswith("/"):
            match = re.match(
                r"^/([A-Za-z0-9_]+)",
                text
            )

            if match:
                command = match.group(1).lower()

                for registered, handler in self._command_handlers:
                    if registered == command:
                        try:
                            await self._run_handler(
                                handler,
                                event
                            )
                        except Exception as exc:
                            print(
                                "[martsor] Command handler error:",
                                exc
                            )

    async def _dispatch_callback(self, event):
        for handler in self._callback_handlers:
            try:
                await self._run_handler(
                    handler,
                    event
                )
            except Exception as exc:
                print(
                    "[martsor] Callback handler error:",
                    exc
                )

    def _install_events(self):
        if self._events_installed:
            return

        @self.client.on(self._events.NewMessage)
        async def _message_event(event):
            await self._dispatch_message(event)

        callback_event = getattr(
            self._events,
            "CallbackQuery",
            None
        )

        if callback_event is not None:

            @self.client.on(callback_event)
            async def _callback_event(event):
                await self._dispatch_callback(event)

        self._events_installed = True

    # ============================================================
    # Connection
    # ============================================================

    async def start(self, *args, **kwargs):
        self._install_events()

        result = self.client.start(
            *args,
            **kwargs
        )

        if inspect.isawaitable(result):
            result = await result

        self._started = True

        return result

    async def run_until_disconnected(self):
        result = self.client.run_until_disconnected()

        if inspect.isawaitable(result):
            return await result

        return result

    async def run(self, *args, **kwargs):
        await self.start(
            *args,
            **kwargs
        )

        return await self.run_until_disconnected()

    async def disconnect(self):
        method = getattr(
            self.client,
            "disconnect",
            None
        )

        if method is None:
            return None

        return await self._call(method)

    # ============================================================
    # Account
    # ============================================================

    async def get_me(self):
        return await self._call_method(
            "get_me"
        )

    # ============================================================
    # Messaging
    # ============================================================

    async def send_message(
        self,
        entity,
        message,
        buttons=None,
        **kwargs
    ):
        """
        Send a message from the user account.

        Martsor buttons are automatically converted
        to the native SPlusthon markup.
        """

        if buttons is not None:
            buttons = self._convert_buttons(
                buttons
            )

            kwargs["buttons"] = buttons

        return await self._call_method(
            "send_message",
            entity,
            message,
            **kwargs
        )

    async def send_file(
        self,
        entity,
        file,
        buttons=None,
        **kwargs
    ):
        """
        Send a file from the user account.

        Buttons can be supplied in the same format
        used by send_message().
        """

        if buttons is not None:
            buttons = self._convert_buttons(
                buttons
            )

            kwargs["buttons"] = buttons

        return await self._call_method(
            "send_file",
            entity,
            file,
            **kwargs
        )

    async def get_messages(
        self,
        entity,
        **kwargs
    ):
        return await self._call_method(
            "get_messages",
            entity,
            **kwargs
        )

    async def edit_message(
        self,
        entity,
        message,
        buttons=None,
        **kwargs
    ):
        if buttons is not None:
            buttons = self._convert_buttons(
                buttons
            )

            kwargs["buttons"] = buttons

        return await self._call_method(
            "edit_message",
            entity,
            message,
            **kwargs
        )

    async def delete_messages(
        self,
        entity,
        messages,
        **kwargs
    ):
        return await self._call_method(
            "delete_messages",
            entity,
            messages,
            **kwargs
        )

    async def forward_messages(
        self,
        entity,
        messages,
        from_peer,
        **kwargs
    ):
        return await self._call_method(
            "forward_messages",
            entity,
            messages,
            from_peer,
            **kwargs
        )

    # ============================================================
    # Entities
    # ============================================================

    async def get_entity(self, entity):
        return await self._call_method(
            "get_entity",
            entity
        )

    async def get_input_entity(self, entity):
        return await self._call_method(
            "get_input_entity",
            entity
        )

    # ============================================================
    # Participants
    # ============================================================

    async def iter_participants(
        self,
        entity,
        **kwargs
    ):
        method = getattr(
            self.client,
            "iter_participants",
            None
        )

        if method is None:
            raise AttributeError(
                "Martsor backend does not provide "
                "iter_participants"
            )

        result = method(
            entity,
            **kwargs
        )

        if hasattr(result, "__aiter__"):
            async for user in result:
                yield user
        else:
            for user in result:
                yield user

    # ============================================================
    # Permissions
    # ============================================================

    async def edit_permissions(
        self,
        chat,
        user,
        **permissions
    ):
        return await self._call_method(
            "edit_permissions",
            chat,
            user,
            **permissions
        )

    async def edit_admin(
        self,
        chat,
        user,
        **kwargs
    ):
        return await self._call_method(
            "edit_admin",
            chat,
            user,
            **kwargs
        )

    async def ban(
        self,
        chat,
        user,
        **kwargs
    ):
        return await self.edit_permissions(
            chat,
            user,
            view_messages=False,
            **kwargs
        )

    async def unban(
        self,
        chat,
        user,
        **kwargs
    ):
        return await self.edit_permissions(
            chat,
            user,
            view_messages=True,
            **kwargs
        )

    async def mute(
        self,
        chat,
        user,
        **kwargs
    ):
        return await self.edit_permissions(
            chat,
            user,
            send_messages=False,
            **kwargs
        )

    async def unmute(
        self,
        chat,
        user,
        **kwargs
    ):
        return await self.edit_permissions(
            chat,
            user,
            send_messages=True,
            **kwargs
        )

    async def promote(
        self,
        chat,
        user,
        **kwargs
    ):
        return await self.edit_admin(
            chat,
            user,
            **kwargs
        )

    async def demote(
        self,
        chat,
        user,
        **kwargs
    ):
        return await self.edit_admin(
            chat,
            user,
            **kwargs
        )