from solution import only_hex


def test_valid():
    assert only_hex("DEADbeef") is True, "Upper AND lower case a-f are hex: the class needs both a-f and A-F."
    assert only_hex("0123456789") is True, "Plain digits are hex digits too."
    assert only_hex("ff8800") is True, "A colour code like ff8800 is valid hex."
    assert only_hex("a") is True, "A single hex digit is fine."


def test_bad_letter():
    assert only_hex("12g4") is False, "'g' is past 'f'. Check every character: use fullmatch, not search or match."
    assert only_hex("abcdefg") is False, "The LAST character 'g' is invalid. re.match(r'[0-9a-fA-F]+') would wrongly accept this."
    assert only_hex("xff") is False, "The FIRST character 'x' is invalid."


def test_empty():
    assert only_hex("") is False, "The empty string is not a hex number: use + (one or more), not *."


def test_prefix_and_spaces():
    assert only_hex("0x1F") is False, "No '0x' prefix: 'x' is not a hex digit."
    assert only_hex("ff ") is False, "A trailing space is not a hex digit."
    assert only_hex(" ff") is False, "A leading space is not a hex digit."
    assert only_hex("f f") is False, "A space in the middle is not a hex digit."


def test_trailing_newline():
    assert only_hex("abc\n") is False, "'abc\\n' ends in a newline. A pattern ending in $ accepts it ($ matches before a final newline); fullmatch does not."


def test_returns_bool():
    assert type(only_hex("ab")) is bool, "Return True/False, not a Match object."
    assert type(only_hex("zz")) is bool, "Return False, not None."
