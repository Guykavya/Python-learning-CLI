from solution import has_digit


def test_digit_in_middle_or_end():
    assert has_digit("room 101") is True, "'room 101' has digits. re.search scans the WHOLE string, not just the start."
    assert has_digit("version2") is True, "The digit is the last character: re.search must look at every position."
    assert has_digit("a1b") is True, "A digit between letters still counts."


def test_digit_at_start():
    assert has_digit("7up") is True, "A digit at position 0 counts."


def test_no_digit():
    assert has_digit("no numbers") is False, "No digit at all: return False."
    assert has_digit("one two three") is False, "Number WORDS are not digits: \\d matches the characters 0-9."
    assert has_digit("!@#$%^&*()_+-=") is False, "Symbols are not digits."


def test_empty_string():
    assert has_digit("") is False, "The empty string has no digit. Return False, not None."


def test_returns_real_bool():
    result = has_digit("abc 9")
    assert type(result) is bool, f"Return a bool, not {type(result).__name__}. re.search gives a Match object or None: compare with 'is not None' or wrap in bool()."
    result = has_digit("abc")
    assert type(result) is bool, f"Return False, not {result!r}. None is falsy, but the task asks for a real bool."
