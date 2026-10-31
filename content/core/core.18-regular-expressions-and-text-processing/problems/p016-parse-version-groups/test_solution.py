from solution import parse_version


def test_plain_and_with_v():
    assert parse_version("1.2.3") == (1, 2, 3), "Three groups (\\d+)\\.(\\d+)\\.(\\d+) give '1', '2', '3'. Convert each to int."
    assert parse_version("v1.2.3") == (1, 2, 3), "An optional 'v' may come first: [vV]? before the first group."
    assert parse_version("V4.0.12") == (4, 0, 12), "A capital 'V' is allowed too."


def test_returns_ints_in_a_tuple():
    result = parse_version("10.20.30")
    assert isinstance(result, tuple), "Return a tuple, not a list or the Match object."
    assert all(isinstance(x, int) for x in result), "m.groups() gives strings like '10'. Convert each with int()."
    assert result == (10, 20, 30), "Each part can have several digits: use \\d+, not \\d."


def test_leading_zeros_and_whitespace():
    assert parse_version("01.002.3") == (1, 2, 3), "int('002') is 2, so leading zeros are fine."
    assert parse_version("  v2.5.9\n") == (2, 5, 9), "Strip whitespace at both ends before matching."


def test_wrong_number_of_parts():
    assert parse_version("1.2") is None, "Only two parts: the third group cannot match, so return None."
    assert parse_version("1.2.3.4") is None, "Four parts: re.search or re.match accept '1.2.3' at the start. Use re.fullmatch so the WHOLE string must fit."
    assert parse_version("1") is None, "A single number is not a version."


def test_extra_text_rejected():
    assert parse_version("v1.2.3-beta") is None, "Text after the patch number must make it fail: re.match stops early, re.fullmatch does not."
    assert parse_version("version 1.2.3") is None, "Only a single v/V may come before the numbers. Did you use re.search?"
    assert parse_version("1.2.3 4") is None, "Space inside the string is not stripped: '1.2.3 4' is not a version."


def test_dot_must_be_escaped():
    assert parse_version("1x2x3") is None, "A bare . matches any character, so '1x2x3' slips through. Escape it: \\."
    assert parse_version("1..3") is None, "Every part needs at least one digit: \\d+ (one or more), not \\d* (zero or more)."


def test_signs_and_empty():
    assert parse_version("-1.2.3") is None, "A minus sign is not a digit, so this is not a version."
    assert parse_version("") is None, "The empty string is not a version."
    assert parse_version("vv1.2.3") is None, "Only ONE optional v: [vV]? not [vV]*."
