from solution import longest


def test_example():
    assert longest("fig", "banana", "kiwi") == "banana"


def test_tie_first_wins():
    assert longest("cat", "dog", "emu") == "cat", (
        "On a tie return the FIRST word. Replace the best only when a word is strictly longer (>), not >=.")
    assert longest("ab", "abcd", "wxyz") == "abcd"


def test_one():
    assert longest("solo") == "solo"


def test_none():
    assert longest() == "", "With no arguments words is (); return the empty string, do not crash."


def test_spread():
    assert longest(*"the quick brown fox".split()) == "quick"


def test_empty_strings():
    assert longest("", "", "") == "", "Three empty strings: the longest is ''."
    assert longest("", "a") == "a"
