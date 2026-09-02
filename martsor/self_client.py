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
        pip install "martsor[self]"
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
                'pip install "martsor[self]"'
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
        """
        Call sync or async functions safely.
        """

        result = function(
            *args,
            **kwargs
        )

        if inspect.isawaitable(result):
            return await result

        return result

    async def _call_method(
        self,
        name,
        *args,
        **kwargs
    ):
        """
        Call a method from the underlying SPlusthon client.
        """

        method = getattr(
            self.client,
            name,
            None
        )

        if method is None:
            raise AttributeError(
                "SPlusthon does not provide method: "
                + name
            )

        return await self._call(
            method,
            *args,
            **kwargs
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
        """
        Register a message handler.

        Example:

            @client.on_message
            async def handler(event):
                print(event.text)
        """

        def decorator(handler):
            self._message_handlers.append(handler)
            return handler

        if function is not None:
            return decorator(function)

        return decorator

    def on_command(self, command):
        """
        Register a command handler.

        Example:

            @client.on_command("start")
            async def start(event):
                await event.respond("سلام")
        """

        command = command.lstrip("/").lower()

        def decorator(handler):
            self._command_handlers.append(
                (command, handler)
            )
            return handler

        return decorator

    def on_callback(self, function=None):
        """
        Register a callback handler.
        """

        def decorator(handler):
            self._callback_handlers.append(handler)
            return handler

        if function is not None:
            return decorator(function)

        return decorator

    # =========================================================
    # Dispatch
    # =========================================================

    async def _run_handler(
        self,
        handler,
        event
    ):
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

        # Normal messages
        for handler in self._message_handlers:
            await self._run_handler(
                handler,
                event
            )

        # Commands
        if text.startswith("/"):
            match = re.match(
                r"^/([A-Za-z0-9_]+)",
                text
            )

            if match:
                command = match.group(1).lower()

                for registered, handler in self._command_handlers:
                    if registered == command:
                        await self._run_handler(
                            handler,
                            event
                        )

    async def _dispatch_callback(self, event):
        for handler in self._callback_handlers:
            await self._run_handler(
                handler,
                event
            )

    # =========================================================
    # Events
    # =========================================================

    def _install_events(self):
        """
        Connect martsor handlers to SPlusthon.
        """

        if self._events_installed:
            return

        @self.client.on(self._events.NewMessage)
        async def _message_event(event):
            await self._dispatch_message(event)

        self._events_installed = True

    # =========================================================
    # Start / Stop
    # =========================================================

    async def start(self, *args, **kwargs):
        """
        Start the Self Client.

        On the first login, SPlusthon may ask
        for authentication information.
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
        """
        Keep the client running.
        """

        result = self.client.run_until_disconnected()

        if inspect.isawaitable(result):
            return await result

        return result

    async def run(self, *args, **kwargs):
        """
        Start and run the client.
        """

        await self.start(
            *args,
            **kwargs
        )

        return await self.run_until_disconnected()

    async def disconnect(self):
        """
        Disconnect the client.
        """

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
        """
        Get current account information.
        """

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
        """
        Send a message.
        """

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
        """
        Send a file.
        """

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
        """
        Get messages.
        """

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
        """
        Edit a message.
        """

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
        """
        Delete messages.
        """

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
        """
        Forward messages.
        """

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
        """
        Resolve an entity.
        """

        return await self._call_method(
            "get_entity",
            entity
        )

    async def get_input_entity(self, entity):
        """
        Resolve an input entity.
        """

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

        Example:

            async for user in client.iter_participants(chat):
                print(user.id)
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
        """
        Edit group permissions for a user.
        """

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
        """
        Edit administrator rights.
        """

        return await self._call_method(
            "edit_admin",
            chat,
            user,
            **kwargs
        )

    async def ban(
       