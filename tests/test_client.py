from martsor import (
    Bot,
    Button,
    InlineKeyboard,
    Update,
)


def test_keyboard():
    keyboard = InlineKeyboard([
        [
            Button(
                "Test",
                callback_data="test",
            )
        ]
    ])

    result = keyboard.to_dict()

    assert result == {
        "inline_keyboard": [
            [
                {
                    "text": "Test",
                    "callback_data": "test",
                }
            ]
        ]
    }


def test_update():
    data = {
        "update_id": 1,
        "message": {
            "message_id": 10,
            "from": {
                "id": 123,
                "is_bot": False,
                "first_name": "Ali",
            },
            "chat": {
                "id": 456,
                "type": "private",
            },
            "text": "hello",
        },
    }

    update = Update.from_dict(data)

    assert update.update_id == 1
    assert update.text == "hello"
    assert update.chat_id == 456
    assert update.message_id == 10


def test_callback():
    data = {
        "update_id": 2,
        "callback_query": {
            "id": "callback-1",
            "from": {
                "id": 123,
                "is_bot": False,
                "first_name": "Ali",
            },
            "data": "about",
            "message": {
                "message_id": 20,
                "chat": {
                    "id": 456,
                    "type": "private",
                },
            },
        },
    }

    update = Update.from_dict(data)

    assert update.data == "about"
    assert update.callback_query_id == "callback-1"
    assert update.chat_id == 456


def test_bot():
    bot = Bot("TEST_TOKEN")

    assert bot.token == "TEST_TOKEN"
    assert bot.base_url == "https://api.splus.ir"


if __name__ == "__main__":
    test_keyboard()
    test_update()
    test_callback()
    test_bot()

    print("All tests passed!")