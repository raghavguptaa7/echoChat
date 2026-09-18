from app.parser import parse_chat


def test_parse_chat():
    chat = """18/09/26, 10:30 PM - Aman: bhai kya kar raha
18/09/26, 10:31 PM - Raghav: kuch nahi bro
18/09/26, 10:32 PM - Aman: kal college aa raha?"""

    messages = parse_chat(chat)

    assert len(messages) == 3
    assert messages[0]["sender"] == "Aman"
    assert messages[0]["message"] == "bhai kya kar raha"
    assert messages[1]["sender"] == "Raghav"