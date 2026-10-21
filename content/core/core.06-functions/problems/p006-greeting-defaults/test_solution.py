from solution import make_greeting


def test_defaults():
    assert make_greeting("Asha") == "Hello, Asha!", "With only a name, use both defaults: 'Hello' and '!'."


def test_positional_greeting():
    assert make_greeting("Ravi", "Welcome") == "Welcome, Ravi!", "The second positional argument is the greeting."


def test_keyword_punctuation_only():
    assert make_greeting("Meena", punctuation="?") == "Hello, Meena?", (
        "Passing only punctuation= by keyword must keep the default greeting.")


def test_all_keywords_any_order():
    assert make_greeting(greeting="Hi", name="Kiran") == "Hi, Kiran!", (
        "Keyword arguments can come in any order. Are your parameters named name, greeting, punctuation?")


def test_all_positional():
    assert make_greeting("Zoya", "Hey", "...") == "Hey, Zoya...", "No space before the punctuation."


def test_empty_name():
    assert make_greeting("") == "Hello, !", "An empty name still gives the comma and punctuation."
