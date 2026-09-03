"""
martsor Self Client.

User account client for Soroush Plus.
Version: 0.3.0
"""

import inspect
import re


class SelfClient:
    """
    Client for Soroush Plus user accounts.

    Requires:
        pip install SPlusthon
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
                "SelfClient requires SPlusthon.\n"
                "Install it with:\n"
                "pip install SPlusthon"
            ) from exc

        self._events = events
        self._StringSession = StringSession

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

    # =========================================================
    # Internal
    # =========================================================

    async def _call(self, function, *args, **kwargs):
        """Call sync or async functions safely."""

        result = function(*args, **kwargs)

        if inspect.isawaitable(result):
            return await result

        return result

    async def _call_method(self, name, *args, **kwargs):
        """Call a method from the SPlusthon client."""

        method = getattr(self.client, name, None)

        if method is None:
            raise AttributeError(
                "SPlusthon does not provide method: " + name
            )

        return await self._call(
            method,
            *args,
            **kwargs
        )

    # =========================================================
    # Report helpers
    # =========================================================

    @staticmethod
    def _get_report_reason(reason):
        """Convert a reason name to a SPlusthon report reason."""

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
            reason.strip()
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

    # =========================================================
    # Report message
    # =========================================================

    async def report_message(
        self,
        entity,
        message_id,
        reason="spam",
        message=""
    ):
        """
        Report one message.

        Example:

            await client.report_message(
                "@username",
                12345,
                reason="spam",
                message="This is spam"
            )
        """

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

    # =========================================================
    # Report peer
    # =========================================================

    async def report_peer(
        self,
        entity,
        reason="spam",
        message=""
    ):
        """
        Report a user, group or channel.

        Example:

            await client.report_peer(
                "@username",
                reason="fake",
                message="Fake account"
            )
        """

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

    # =========================================================
    # Report spam
    # =========================================================

    async def report_spam(self, entity):
        """
        Report a peer as spam.

        Example:

            await client.report_spam("@username")
        """

        from splusthon.tl.functions.messages import ReportSpamRequest

        peer = await self.get_input_entity(entity)

        request = ReportSpamRequest(
            peer=peer
        )

        return await self._call(
            self.client,
            request
        )

    # =========================================================
    # Properties
    # =========================================================

    @property
    def session(self):
        """Return the current session."""

        return self.client.session

    # =========================================================
    # Event system
    # =========================================================

    def on_message(self, function=None):
        """Register a message handler."""

        def decorator(handler):
            self._message_handlers.append(handler)
            return handler

        if function is not None:
            return decorator(function)

        return decorator

    def on_command(self, command):
        """Register a command handler."""

        command = command.lstrip("/").lower()

        def decorator(handler):
            self._command_handlers.append(
                (command, handler)
            )
            return handler

        return decorator

    def on_callback(self, function=None):
        """Register a callback handler."""

        def decorator(handler):
            self._callback_handlers.append(handler)
            return handler

        if function is not None:
            return decorator(function)

        return decorator

    # =========================================================
    # Dispatch
    # =========================================================

    async def _run_handler(self, handler, event):
        result = handler(event)

        if inspect.isawaitable(result):
            return await result

        return result

    async def _dispatch_message(self, event):
        text = getattr(event, "text", None)

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

    # =========================================================
    # Events
    # =========================================================

    def _install_events(self):
        """Connect martsor handlers to SPlusthon."""

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

    # =========================================================
    # Start / Stop
    # =========================================================

    async def start(self, *args, **kwargs):
        """
        Start the Self Client.

        SPlusthon may ask for authentication
        information on first login.
        """

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
        """Keep the client running."""

        result = self.client.run_until_disconnected()

        if inspect.isawaitable(result):
            return await result

        return result

    async def run(self, *args, **kwargs):
        """Start and run the client."""

        await self.start(
            *args,
            **kwargs
        )

        return await self.run_until_disconnected()

    async def disconnect(self):
        """Disconnect the client."""

        method = getattr(
            self.client,
            "disconnect",
            None
        )

        if method is None:
            return None

        return await self._call(method)

    # =========================================================
    # Account
    # =========================================================

    async def get_me(self):
        """Get current account information."""

        return await self._call_method(
            "get_me"
        )

    # =========================================================
    # Messaging
    # =========================================================

    async def send_message(
        self,
        entity,
        message,
        **kwargs
    ):
        """Send a message."""

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
        **kwargs
    ):
        """Send a file."""

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
        """Get messages."""

        return await self._call_method(
            "get_messages",
            entity,
            **kwargs
        )

    async def edit_message(
        self,
        entity,
        message,
        **kwargs
    ):
        """Edit a message."""

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
        """Delete messages."""

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
        """Forward messages."""

        return await self._call_method(
            "forward_messages",
            entity,
            messages,
            from_peer,
            **kwargs
        )

    # =========================================================
    # Entities
    # =========================================================

    async def get_entity(self, entity):
        """Resolve an entity."""

        return await self._call_method(
            "get_entity",
            entity
        )

    async def get_input_entity(self, entity):
        """Resolve an input entity."""

        return await self._call_method(
            "get_input_entity",
            entity
        )

    # =========================================================
    # Group management
    # =========================================================

    async def iter_participants(
        self,
        entity,
        **kwargs
    ):
        """
        Iterate over group participants.
        """

        method = getattr(
            self.client,
            "iter_participants",
            None
        )

        if method is None:
            raise AttributeError(
                "SPlusthon does not provide "
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

    async def edit_permissions(
        self,
        chat,
        user,
        **permissions
    ):
        """Edit group permissions for a user."""

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
        """Edit administrator rights."""

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
        """Ban a user from a group."""

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
        """Unban a user from a group."""

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
        """Restrict a user from sending messages."""

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
        """Allow a user to send messages."""

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
        """Promote a user to administrator."""

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
        """Remove administrator privileges."""

        return await self.edit_admin(
            chat,
            user,
            is_admin=False,
            **kwargs
        )