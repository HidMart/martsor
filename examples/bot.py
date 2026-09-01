import asyncio

from martsor import Bot


TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(TOKEN)


@bot.on_message
async def handle_message(update):
    if not update.message:
        return

    print("Chat:", update.message.chat_id)
    print("Text:", update.message.text)


async def main():
    print("martsor 0.1.0")
    print("Bot is ready.")

    # API polling will be connected here
    # after the official update endpoint is confirmed.


if __name__ == "__main__":
    asyncio.run(main())