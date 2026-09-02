# martsor/self_client.py
"""
martsor Self Client
Version: 0.3.0

User-account client for Soroush Plus based on SPlusthon.
"""

import inspect
import re


class SelfClient:
    """
    Client for using a Soroush Plus user account.

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

        self._SoroushClient = SoroushClient
        self._events = events
        self._StringSession = StringSession

        # Empty StringSession = first login
        if session is None:
            session = StringSession()
        elif isinstance(session, str):
            session = StringSession(session)

        client_kwargs = dict(kwargs)

        if api_id is not None:
            client_kwargs["api_id"] = api_id

        if api_hash is not None:
            client_kwargs["api_hash"] = api_hash

        self.client = SoroushClient(
            session,
            **client_kwargs
        )

        self._message_handlers = []
        self._command_handlers = []
        self._callback_handlers = []
        self._started = False

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    async def _call(self, function, *args, **kwargs):
        """
        Supports both async and sync methods from SPlusthon.
        """
        result = function(*args, **kwargs)

        if inspect.isawaitable(result):
            return await result

        return result

    async def _call_method(self, name, *args, **kwargs):
        """
        Call a method on the underlying SPlusthon client.
        """
        function = getattr(self.client, name, None)

        if function is None:
            raise AttributeError(
                "SPlusthon does not provide method: "
                + name
            )

        return await self._call(
            function,
            *args,
            **kwargs
        )

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def session(self):
        """Return the current SPlusthon session."""
        return self.client.session

    @property
    def me(self):
        """Return the current account information."""
        return self.client.get_me()

    # ---------------------------------------------------------
    # Event handlers
    # ---------------------------------------------------------

    def on_message(self, handler=None):
        """
        Register a message handler.

        Example:

            @client.on_message
            async def handler(event):
                print(event.text)
        """

        def decorator(function):
            self._message_handlers.append(function)
            return function

        if handler is not None:
            return decorator(handler)

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

        def decorator(function):
            self._command_handlers.append(
                (command, function)
            )
            return function

        return decorator

    def on_callback(self, handler=None):
        """
        Register a callback handler.

        This is kept as a generic callback registration
        point for SPlusthon event objects.
        """

        def decorator(function):
            self._callback_handlers.append(function)
            return function

        if handler is not None:
            return decorator(handler)

        return decorator

    # ---------------------------------------------------------
    # Internal event dispatch
    # ---------------------------------------------------------

    async def _run_handler(self, handler, event):
        result = handler(event)

        if inspect.isawaitable(result):
            return await result

        return result

    async def _dispatch_message(self, event):
        text = getattr(event, "text", None) or ""

        # Normal message handlers
        for handler in self._message_handlers:
            await self._run_handler(
                handler,
                event
            )

        # Command handlers
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

    # ---------------------------------------------------------
    # Start / Stop
    # ---------------------------------------------------------

    def _install_events(self):
        """
        Connect martsor handlers to SPlusthon.
        """

        @self.client.on(self._events.NewMessage)
        async def _new_message(event):
            await self._dispatch_message(event)

    async def start(self, *args, **kwargs):
        """
        Start/login the Self Client.

        On first launch SPlusthon may request authentication.
        """

        if not self._started:
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
        Keep the client running until disconnected.
        """

        result = self.client.run_until_disconnected()

        if inspect.isawaitable(result):
            return await result

        return result

    async def run(self, *args, **kwargs):
        """
        Start the client and keep it running.
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

        function = getattr(
            self.client,
            "disconnect",
            None
        )

        if function is None:
            return None

        return await self._call(function)

    # ---------------------------------------------------------
    # Messaging
    # ---------------------------------------------------------

    async def send_message(
        self,
        entity,
        message,
        **kwargs
    ):
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

    async def iter_messages(
        self,
        entity,
        **kwargs
    ):
        """
        Async iterator for messages.
        """

        function = getattr(
            self.client,
            "iter_messages",
            None
        )

        if function is None:
            raise AttributeError(
                "SPlusthon does not provide iter_messages"
            )

        result = function(
            entity,
            **kwargs
        )

        if hasattr(result, "__aiter__"):
            async for item in result:
                yield item
        else:
            for item in result:
                yield item

    async def edit_message(
        self,
        entity=None,
        message=None,
        **kwargs
    ):
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

    # ---------------------------------------------------------
    # Entity
    # ---------------------------------------------------------

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

    async def get_me(self):
        return await self._call_method(
            "get_me"
        )

    # ---------------------------------------------------------
    # Group management
    # ---------------------------------------------------------

    async def iter_participants(
        self,
        entity,
        **kwargs
    ):
        """
        Iterate over group members.

        Example:

            async for user in client.iter_participants(chat):
                print(user.id)
        """

        function = getattr(
            self.client,
            "iter_participants",
            None
        )

        if function is None:
            raise AttributeError(
                "SPlusthon does not provide "
                "iter_participants"
            )

        result = function(
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
        Change a user's group permissions.

        Example:

            await client.edit_permissions(
                chat,
                user,
                send_messages=False
            )
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
        Change administrator status/rights.
        """

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
        """
        Ban a user from a group.

        Uses SPlusthon's permission system.
        """

        permissions = {
            "view_messages": False
        }

        permissions.update(kwargs)

        return await self.edit_permissions(
            chat,
            user,
            **permissions
        )

    async def unban(
        self,
        chat,
        user,
        **kwargs
    ):
        """
        Remove the view restriction from a user.
        """

        permissions = {
            "view_messages": True
        }

        permissions.update(kwargs)

        return await self.edit_permissions(
            chat,
            user,
            **permissions
        )

    async def mute(
        self,
        chat,
        user,
        **kwargs
    ):
        """
        Restrict a user's ability to send messages.
        """

        permissions = {
            "send_messages": False
        }

        permissions.update(kwargs)

        return await self.edit_permissions(
            chat,
            user,
            **permissions
        )

    async def unmute(
        self,
        chat,
        user,
        **kwargs
    ):
        """
        Restore a user's message permission.
        """

        permissions = {
            "send_messages": True
        }

        permissions.update(kwargs)

        return await self.edit_permissions(
            chat,
            user,
            **permissions
        )

    async def promote(
        self,
        chat,
        user,
        **kwargs
    ):
        """
        Promote a user to administrator.

        Extra administrator rights can be passed through kwargs.
        """

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
        """
        Remove administrator status.
        """

        return await self.edit_admin(
            chat,
            user,
            is_admin=False,
            **kwargs
        )

    async def kick(
        self,
        chat,
        user,
        **kwargs
    ):
        """
        Remove a user from a group.

        This uses the permission API available in SPlusthon.
        """

        permissions = {
            "view_messages": False
        }

        permissions.update(kwargs)

        return await self.edit_permissions(
            chat,
            user,
            **permissions
        )

    # ---------------------------------------------------------
    # Generic access
    # ---------------------------------------------------------

    def __getattr__(self, name):
        """
        Forward unknown attributes/methods to SPlusthon.

        This allows advanced SPlusthon functionality without
        requiring a new wrapper for every API method.
        """

        client = self.__dict__.get("client")

        if client is None:
            raise AttributeError(name)

        return getattr(client, name)