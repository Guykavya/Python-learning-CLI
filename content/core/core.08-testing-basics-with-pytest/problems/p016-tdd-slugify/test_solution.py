from solution import slugify


def test_1_lower_case():
    assert slugify("Hello") == "hello", "Rule 1: turn the text to lower case."


def test_2_words_joined_with_hyphen():
    assert slugify("Hello World") == "hello-world", "Rule 2: join the words with a single '-'."


def test_3_extra_spaces_ignored():
    assert slugify("  hello   world  ") == "hello-world", "Rule 3: spaces at the ends and doubled spaces vanish."


def test_4_punctuation_dropped():
    assert slugify("Hello, World!") == "hello-world", "Rule 4: keep only letters and digits inside a word."
    assert slugify("Python 3.14") == "python-314", "The dot in 3.14 is dropped but the digits stay."


def test_5_empty_words_disappear():
    assert slugify("a - b") == "a-b", "Rule 5: a lone '-' becomes an empty word, which must be skipped."
    assert slugify("Rock & Roll!") == "rock-roll", "The '&' is a word of its own; it must not leave '--'."


def test_6_empty_text():
    assert slugify("") == "", "Rule 6: empty text gives an empty slug."
    assert slugify("   ") == "", "Only spaces: also an empty slug."
    assert slugify("!!!") == "", "Only punctuation: also an empty slug."
