import asyncio
import inspect
import json
import time
import urllib.error
import urllib.request
import uuid

from .errors import APIError
from .types import Update


class Client:
    """Low-level client for the Soroush Plus Bot API."""

    def __init__(
        self,
        token,
        base_url="https://api.splus.ir",
        timeout=60,
        max_retries=3,
    ):
        if not token:
            raise ValueError("Bot token is required.")

        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    def _build_url(self, method):
        return (
            "{}/bot{}/{}".format(
                self.base_url,
                self.token,
                method.strip("/"),
            )
        )

    def _serialize(self, value):
        if hasattr(value, "to_dict"):
            return value.to_dict()

        if isinstance(value, list):
            return [self._serialize(item) for item in value]

        if isinstance(value, dict):
            return {
                key: self._serialize(item)
                for key, item in value.items()
            }

        return value

    def request(
        self,
        method,
        data=None,
        http_method="POST",
    ):
        url = self._build_url(method)

        if data is None:
            data = {}

        data = self._serialize(data)

        payload = json.dumps(
            data,
            ensure_ascii=False,
        ).encode("utf-8")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "martsor/0.2.0",
        }

        request = urllib.request.Request(
            url=url,
            data=payload,
            headers=headers,
            method=http_method.upper(),
        )

        attempts = 0

        while True:
            try:
                with urllib.request.urlopen(
                    request,
                    timeout=self.timeout,
                ) as response:
                    raw = response.read().decode(
                        "utf-8",
                        errors="replace",
                    )

                    status_code = response.getcode()

                return self._handle_response(
                    raw,
                    status_code,
                )

            except urllib.error.HTTPError as exc:
                body = exc.read().decode(
                    "utf-8",
                    errors="replace",
                )

                try:
                    parsed = json.loads(body)
                except Exception:
                    parsed = None

                retry_after = None

                if isinstance(parsed, dict):
                    parameters = parsed.get(
                        "parameters",
                        {},
                    )

                    if isinstance(parameters, dict):
                        retry_after = parameters.get(
                            "retry_after"
                        )

                if (
                    exc.code == 429
                    and retry_after is not None
                    and attempts < self.max_retries
                ):
                    attempts += 1
                    time.sleep(float(retry_after))
                    continue

                raise APIError(
                    "API request failed: HTTP {}".format(
                        exc.code
                    ),
                    error_code=(
                        parsed.get("error_code")
                        if isinstance(parsed, dict)
                        else None
                    ),
                    status_code=exc.code,
                    response=parsed or body,
                    retry_after=retry_after,
                )

            except urllib.error.URLError as exc:
                raise APIError(
                    "Could not connect to Soroush Plus API: {}".format(
                        exc.reason
                    )
                ) from exc

    def _handle_response(self, raw, status_code):
        if not raw:
            return None

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            return raw

        if isinstance(result, dict):
            if result.get("ok") is False:
                parameters = result.get(
                    "parameters",
                    {},
                )

                retry_after = None

                if isinstance(parameters, dict):
                    retry_after = parameters.get(
                        "retry_after"
                    )

                raise APIError(
                    result.get(
                        "description",
                        "Soroush Plus API error",
                    ),
                    error_code=result.get("error_code"),
                    status_code=status_code,
                    response=result,
                    retry_after=retry_after,
                )

            return result.get(
                "result",
                result,
            )

        return result

    def get_me(self):
        return self.request("getMe")

    def get_updates(
        self,
        offset=None,
        limit=100,
        timeout=30,
        allowed_updates=None,
    ):
        data = {
            "limit": limit,
            "timeout": timeout,
        }

        if offset is not None:
            data["offset"] = offset

        if allowed_updates is not None:
            data["allowed_updates"] = allowed_updates

        return self.request(
            "getUpdates",
            data,
        )

    def send_message(
        self,
        chat_id,
        text,
        parse_mode=None,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "text": text,
        }

        if parse_mode is not None:
            data["parse_mode"] = parse_mode

        if reply_to_message_id is not None:
            data["reply_to_message_id"] = (
                reply_to_message_id
            )

        if reply_markup is not None:
            data["reply_markup"] = self._serialize(
                reply_markup
            )

        return self.request(
            "sendMessage",
            data,
        )

    def send_photo(
        self,
        chat_id,
        photo,
        caption=None,
        parse_mode=None,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "photo": photo,
        }

        self._add_common_send_params(
            data,
            caption,
            parse_mode,
            reply_to_message_id,
            reply_markup,
        )

        return self.request(
            "sendPhoto",
            data,
        )

    def send_document(
        self,
        chat_id,
        document,
        caption=None,
        parse_mode=None,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "document": document,
        }

        self._add_common_send_params(
            data,
            caption,
            parse_mode,
            reply_to_message_id,
            reply_markup,
        )

        return self.request(
            "sendDocument",
            data,
        )

    def send_video(
        self,
        chat_id,
        video,
        caption=None,
        parse_mode=None,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "video": video,
        }

        self._add_common_send_params(
            data,
            caption,
            parse_mode,
            reply_to_message_id,
            reply_markup,
        )

        return self.request(
            "sendVideo",
            data,
        )

    def send_audio(
        self,
        chat_id,
        audio,
        caption=None,
        parse_mode=None,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "audio": audio,
        }

        self._add_common_send_params(
            data,
            caption,
            parse_mode,
            reply_to_message_id,
            reply_markup,
        )

        return self.request(
            "sendAudio",
            data,
        )

    def send_voice(
        self,
        chat_id,
        voice,
        caption=None,
        parse_mode=None,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "voice": voice,
        }

        self._add_common_send_params(
            data,
            caption,
            parse_mode,
            reply_to_message_id,
            reply_markup,
        )

        return self.request(
            "sendVoice",
            data,
        )

    def send_animation(
        self,
        chat_id,
        animation,
        caption=None,
        parse_mode=None,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "animation": animation,
        }

        self._add_common_send_params(
            data,
            caption,
            parse_mode,
            reply_to_message_id,
            reply_markup,
        )

        return self.request(
            "sendAnimation",
            data,
        )

    def send_sticker(
        self,
        chat_id,
        sticker,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "sticker": sticker,
        }

        if reply_to_message_id is not None:
            data["reply_to_message_id"] = (
                reply_to_message_id
            )

        if reply_markup is not None:
            data["reply_markup"] = self._serialize(
                reply_markup
            )

        return self.request(
            "sendSticker",
            data,
        )

    def send_location(
        self,
        chat_id,
        latitude,
        longitude,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
        }

        if reply_to_message_id is not None:
            data["reply_to_message_id"] = (
                reply_to_message_id
            )

        if reply_markup is not None:
            data["reply_markup"] = self._serialize(
                reply_markup
            )

        return self.request(
            "sendLocation",
            data,
        )

    def send_contact(
        self,
        chat_id,
        phone_number,
        first_name,
        last_name=None,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "phone_number": phone_number,
            "first_name": first_name,
        }

        if last_name is not None:
            data["last_name"] = last_name

        if reply_to_message_id is not None:
            data["reply_to_message_id"] = (
                reply_to_message_id
            )

        if reply_markup is not None:
            data["reply_markup"] = self._serialize(
                reply_markup
            )

        return self.request(
            "sendContact",
            data,
        )

    def send_media_group(
        self,
        chat_id,
        media,
        reply_to_message_id=None,
    ):
        data = {
            "chat_id": chat_id,
            "media": media,
        }

        if reply_to_message_id is not None:
            data["reply_to_message_id"] = (
                reply_to_message_id
            )

        return self.request(
            "sendMediaGroup",
            data,
        )

    def forward_message(
        self,
        chat_id,
        from_chat_id,
        message_id,
    ):
        return self.request(
            "forwardMessage",
            {
                "chat_id": chat_id,
                "from_chat_id": from_chat_id,
                "message_id": message_id,
            },
        )

    def copy_message(
        self,
        chat_id,
        from_chat_id,
        message_id,
    ):
        return self.request(
            "copyMessage",
            {
                "chat_id": chat_id,
                "from_chat_id": from_chat_id,
                "message_id": message_id,
            },
        )

    def get_file(self, file_id):
        return self.request(
            "getFile",
            {
                "file_id": file_id,
            },
        )

    def delete_message(
        self,
        chat_id,
        message_id,
    ):
        return self.request(
            "deleteMessage",
            {
                "chat_id": chat_id,
                "message_id": message_id,
            },
        )

    def get_chat(self, chat_id):
        return self.request(
            "getChat",
            {
                "chat_id": chat_id,
            },
        )

    def edit_message_text(
        self,
        chat_id,
        message_id,
        text,
        parse_mode=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
        }

        if parse_mode is not None:
            data["parse_mode"] = parse_mode

        if reply_markup is not None:
            data["reply_markup"] = self._serialize(
                reply_markup
            )

        return self.request(
            "editMessageText",
            data,
        )

    def edit_message_caption(
        self,
        chat_id,
        message_id,
        caption,
        parse_mode=None,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "caption": caption,
        }

        if parse_mode is not None:
            data["parse_mode"] = parse_mode

        if reply_markup is not None:
            data["reply_markup"] = self._serialize(
                reply_markup
            )

        return self.request(
            "editMessageCaption",
            data,
        )

    def edit_message_media(
        self,
        chat_id,
        message_id,
        media,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "media": media,
        }

        if reply_markup is not None:
            data["reply_markup"] = self._serialize(
                reply_markup
            )

        return self.request(
            "editMessageMedia",
            data,
        )

    def edit_message_reply_markup(
        self,
        chat_id,
        message_id,
        reply_markup=None,
    ):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
        }

        if reply_markup is not None:
            data["reply_markup"] = self._serialize(
                reply_markup
            )

        return self.request(
            "editMessageReplyMarkup",
            data,
        )

    def answer_callback_query(
        self,
        callback_query_id,
        text=None,
        show_alert=False,
    ):
        data = {
            "callback_query_id": callback_query_id,
            "show_alert": show_alert,
        }

        if text is not None:
            data["text"] = text

        return self.request(
            "answerCallbackQuery",
            data,
        )

    def set_my_commands(self, commands):
        return self.request(
            "setMyCommands",
            {
                "commands": commands,
            },
        )

    def get_my_commands(self):
        return self.request(
            "getMyCommands"
        )

    def delete_my_commands(self):
        return self.request(
            "deleteMyCommands"
        )

    def set_webhook(
        self,
        url,
        max_connections=40,
        allowed_updates=None,
    ):
        data = {
            "url": url,
            "max_connections": max_connections,
        }

        if allowed_updates is not None:
            data["allowed_updates"] = allowed_updates

        return self.request(
            "setWebhook",
            data,
        )

    def delete_webhook(self):
        return self.request(
            "deleteWebhook"
        )

    def get_webhook_info(self):
        return self.request(
            "getWebhookInfo"
        )

    def _add_common_send_params(
        self,
        data,
        caption,
        parse_mode,
        reply_to_message_id,
        reply_markup,
    ):
        if caption is not None:
            data["caption"] = caption

        if parse_mode is not None:
            data["parse_mode"] = parse_mode

        if reply_to_message_id is not None:
            data["reply_to_message_id"] = (
                reply_to_message_id
            )

        if reply_markup is not None:
            data["reply_markup"] = self._serialize(
                reply_markup
            )


class Bot(Client):
    """High-level Soroush Plus bot."""

    def __init__(
        self,
        token,
        base_url="https://api.splus.ir",
        timeout=60,
        max_retries=3,
    ):
        super().__init__(
            token=token,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        self._message_handlers = []
        self._command_handlers = {}
        self._callback_handlers = []
        self._edited_message_handlers = []

        self._running = False
        self._offset = None
        self.me = None

    def on_message(self, func=None):
        def decorator(handler):
            self._message_handlers.append(handler)
            return handler

        if func is not None:
            return decorator(func)

        return decorator

    def on_command(self, command):
        command = command.lstrip("/")

        def decorator(func):
            self._command_handlers[command] = func
            return func

        return decorator

    def on_callback(self, func=None):
        def decorator(handler):
            self._callback_handlers.append(handler)
            return handler

        if func is not None:
            return decorator(func)

        return decorator

    def on_edited_message(self, func=None):
        def decorator(handler):
            self._edited_message_handlers.append(handler)
            return handler

        if func is not None:
            return decorator(func)

        return decorator

    def _convert_update(self, data):
        return Update.from_dict(data)

    def _get_command(self, text):
        if not text:
            return None

        text = text.strip()

        if not text.startswith("/"):
            return None

        command = text.split()[0][1:]

        if "@" in command:
            command = command.split("@", 1)[0]

        return command.lower()

    async def _call_handler(self, handler, update):
        result = handler(update)

        if inspect.isawaitable(result):
            await result

    async def dispatch(self, data):
        update = self._convert_update(data)

        if update.callback_query is not None:
            for handler in self._callback_handlers:
                await self._call_handler(
                    handler,
                    update,
                )

            return update

        if update.edited_message is not None:
            for handler in self._edited_message_handlers:
                await self._call_handler(
                    handler,
                    update,
                )

        if update.message is not None:
            command = self._get_command(
                update.message.text
            )

            if command in self._command_handlers:
                await self._call_handler(
                    self._command_handlers[command],
                    update,
                )

            for handler in self._message_handlers:
                await self._call_handler(
                    handler,
                    update,
                )

        return update

    def _dispatch_sync(self, data):
        return asyncio.run(
            self.dispatch(data)
        )

    def run(
        self,
        timeout=30,
        limit=100,
        allowed_updates=None,
        retry_delay=3,
    ):
        self._running = True

        print(
            "[martsor 0.2.0] Starting bot..."
        )

        try:
            self.me = self.get_me()

            print(
                "[martsor] Bot connected."
            )

            if isinstance(self.me, dict):
                username = self.me.get(
                    "username"
                )

                if username:
                    print(
                        "[martsor] Logged in as @{}".format(
                            username
                        )
                    )

        except Exception as exc:
            print(
                "[martsor] getMe failed: {}".format(
                    exc
                )
            )

        while self._running:
            try:
                updates = self.get_updates(
                    offset=self._offset,
                    limit=limit,
                    timeout=timeout,
                    allowed_updates=allowed_updates,
                )

                if not updates:
                    continue

                for update in updates:
                    if not isinstance(update, dict):
                        continue

                    update_id = update.get(
                        "update_id"
                    )

                    if update_id is not None:
                        self._offset = update_id + 1

                    try:
                        self._dispatch_sync(update)

                    except Exception as exc:
                        print(
                            "[martsor] Handler error: {}".format(
                                exc
                            )
                        )

            except APIError as exc:
                if exc.error_code == 429:
                    delay = exc.retry_after or retry_delay

                    print(
                        "[martsor] Rate limited. "
                        "Waiting {} seconds...".format(
                            delay
                        )
                    )

                    time.sleep(
                        float(delay)
                    )

                else:
                    print(
                        "[martsor] API error: {}".format(
                            exc
                        )
                    )

                    time.sleep(
                        retry_delay
                    )

            except KeyboardInterrupt:
                print(
                    "\n[martsor] Stopped."
                )
                break

            except Exception as exc:
                print(
                    "[martsor] Error: {}".format(
                        exc
                    )
                )

                time.sleep(
                    retry_delay
                )

        self._running = False

    def stop(self):
        self._running = False