from solution import valid_pin


def test_valid_lengths():
    assert valid_pin("1234") is True, "4 digits is the minimum and is valid."
    assert valid_pin("12345") is True, "5 digits is valid."
    assert valid_pin("123456") is True, "6 digits is the maximum and is valid."
    assert valid_pin("0000") is True, "Zeros are digits too; leading zeros are fine in a PIN."


def test_too_short():
    assert valid_pin("123") is False, "3 digits is too short: the quantifier is {4,6}."
    assert valid_pin("") is False, "The empty string is not a PIN."


def test_too_long():
    assert valid_pin("1234567") is False, "7 digits is too long. re.match or re.search would accept the first 6 digits: use fullmatch."


def test_non_digits():
    assert valid_pin("12a4") is False, "Letters are not allowed."
    assert valid_pin("12 34") is False, "Spaces are not allowed."
    assert valid_pin("-1234") is False, "A sign is not allowed."
    assert valid_pin("abc1234") is False, "re.search would find '1234' inside: the WHOLE string must be the PIN."


def test_trailing_newline():
    assert valid_pin("1234\n") is False, "A trailing newline makes it invalid. A pattern ending in $ accepts it; fullmatch does not."


def test_ascii_digits_only():
    assert valid_pin("१२३४") is False, "These are Devanagari digits. \\d matches them; use [0-9] (or the re.ASCII flag) to allow only 0-9."


def test_returns_bool():
    assert type(valid_pin("9999")) is bool, "Return True, not a Match object."
    assert type(valid_pin("99")) is bool, "Return False, not None."
