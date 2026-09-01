import json
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, Optional

from .errors import APIError
from .types import Message, Update


class Client:
    """Low-level HTTP client for martsor."""

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.splus.ir",
        timeout: int = 30,
    ):
        if not token:
            raise ValueError("Bot token is required.")

        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Send an HTTP request.

        Endpoint paths are intentionally configurable because the
        exact official Soroush Plus Bot API routes should be taken
        directly from the current official documentation.
        """

        url = self.base_url + "/" + endpoint.lstrip("/")

        payload = None

        if data is not None:
            payload = json.dumps(data).encode("utf-8")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token,
            "User-Agent": "martsor/0.1.0",
        }

        request = urllib.request.Request(
            url=url,
            data=payload,
            headers=headers,
            method=method.upper(),
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                raw = response.read().decode("utf-8")

                if not raw:
                    return None

                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return raw

        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")

            raise APIError(
                "API request failed: HTTP {}".format(exc.code),
                status_code=exc.code,
                response=body,
            ) from exc

        except urllib.error.URLError as exc:
            raise APIError(
                "Could not connect to the API: {}".format(exc.reason)
            ) from exc

    def get(self, endpoint: str) -> Any:
        return self.request("GET", endpoint)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self.request("POST", endpoint, data)


class Bot(Client):
    """High-level bot interface."""

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.splus.ir",
        timeout: int = 30,
    ):
        super().__init__(
            token=token,
            base_url=base_url,
            timeout=timeout,
        )

        self._handlers = []

    def on_message(self, func: Callable):
        """Register a message handler."""

        self._handlers.append(func)
        return func

    def _convert_update(self, data: Dict[str, Any]) -> Update:
        """Convert a raw API update into an Update object."""

        message_data = data.get("message")

        message = None

        if isinstance(message_data, dict):
            message = Message(
                chat_id=message_data.get("chat_id"),
                text=message_data.get("text"),
                message_id=message_data.get("message_id"),
                raw=message_data,
            )

        return Update(
            update_id=data.get("update_id"),
            message=message,
            raw=data,
        )

    async def dispatch(self, data: Dict[str, Any]):
        """Dispatch an update to registered handlers."""

        update = self._convert_update(data)

        for handler in self._handlers:
            result = handler(update)

            if hasattr(result, "__await__"):
                await result

    def send_message(
        self,
        chat_id: str,
        text: str,
        endpoint: str = "/sendMessage",
    ):
        """
        Send a text message.

        The default endpoint is a placeholder until the exact
        official endpoint is confirmed from the Soroush Plus docs.
        """

        return self.post(
            endpoint,
            {
                "chat_id": chat_id,
                "text": text,
            },
        )

    def run(self):
        """
        Start the bot.

        Polling implementation will be added after the official
        update/get-updates endpoint is confirmed.
        """

        raise NotImplementedError(
            "Polling will be implemented using the official "
            "Soroush Plus Bot API update endpoint."
        )