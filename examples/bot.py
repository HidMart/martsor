import os

from martsor import Bot, InlineKeyboard


TOKEN = os.environ.get("MARTSOR_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "MARTSOR_TOKEN environment variable is not set."
    )


bot = Bot(TOKEN)


@bot.on_command("start")
def start(update):
    keyboard = InlineKeyboard([
        [
            InlineKeyboard.button(
                "درباره ما",
                callback_data="about",
            ),
            InlineKeyboard.button(
                "راهنما",
                callback_data="help",
            ),
        ],
        [
            InlineKeyboard.url(
                "وب‌سایت",
                "https://example.com",
            )
        ],
    ])

    bot.send_message(
        update.chat_id,
        "سلام! به ربات martsor خوش آمدی.",
        reply_markup=keyboard,
    )


@bot.on_message
def message(update):
    if update.text:
        print(
            "Message:",
            update.text,
        )


@bot.on_callback
def callback(update):
    if update.data == "about":
        bot.answer_callback_query(
            update.callback_query_id,
            "این ربات با martsor ساخته شده است.",
        )

        bot.send_message(
            update.chat_id,
            "کتابخانه martsor برای ساخت ربات سروش‌پلاس است.",
        )

    elif update.data == "help":
        bot.answer_callback_query(
            update.callback_query_id,
            "راهنما ارسال شد.",
        )

        bot.send_message(
            update.chat_id,
            "برای شروع /start را ارسال کنید.",
        )


bot.run()