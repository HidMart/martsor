martsor

Python library for building bots and user clients with the Soroush Plus API.

Version: 0.3.0

Features

Bot

- Soroush Plus Bot API
- Long polling
- getUpdates
- sendMessage
- sendPhoto
- sendDocument
- sendVideo
- sendAudio
- sendVoice
- sendAnimation
- sendSticker
- sendLocation
- sendContact
- sendMediaGroup
- forwardMessage
- copyMessage
- getFile
- getChat
- deleteMessage
- editMessageText
- editMessageCaption
- editMessageMedia
- editMessageReplyMarkup
- InlineKeyboard
- Callback Query
- Reply Keyboard
- Force Reply
- Bot commands
- Webhook API methods
- MarkdownV2 / HTML parse mode support

SelfClient

- Soroush Plus user client
- Login with phone number
- Get current account information
- Send messages
- Send files
- Get messages
- Edit messages
- Delete messages
- Forward messages
- Message event handlers
- Command event handlers
- Callback event handlers

Group Management

- Get group members
- Manage member permissions
- Promote members
- Demote admins
- Ban members
- Unban members
- Mute members
- Unmute members
- Manage group administrators

Installation

Basic installation

pip install martsor

SelfClient

pip install "martsor[self]"

Example

Bot

from martsor import Bot

bot = Bot("YOUR_BOT_TOKEN")

@bot.on_message()
async def handler(message):
    await message.reply("سلام!")

bot.run()

SelfClient

import asyncio
from martsor import SelfClient

async def main():
    client = SelfClient()

    await client.start()

    me = await client.get_me()
    print("Logged in as:", me)

    await client.run_until_disconnected()

asyncio.run(main())

License

MIT License