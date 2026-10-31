from solution import is_mobile


def test_plain_ten_digits():
    assert is_mobile("9876543210") is True, "Ten digits starting with 9 and no prefix is the simplest valid number."
    assert is_mobile("6000000000") is True, "6 is an allowed first digit."
    assert is_mobile("7123456789") is True, "7 is an allowed first digit."


def test_first_digit_rule():
    assert is_mobile("5876543210") is False, "The first digit of the number must be 6-9: use [6-9], not [0-9] or \\d."
    assert is_mobile("0123456789") is False, "Here 0 is the prefix, leaving '123456789' (9 digits starting with 1): invalid."


def test_length():
    assert is_mobile("987654321") is False, "9 digits is too short."
    assert is_mobile("98765432101") is False, "11 digits is too long. Use fullmatch so extra digits fail."


def test_plus91_prefix():
    assert is_mobile("+919876543210") is True, "+91 directly before the number is allowed."
    assert is_mobile("+91 9876543210") is True, "+91 then ONE space is allowed."
    assert is_mobile("+91-9876543210") is True, "+91 then ONE hyphen is allowed."
    assert is_mobile("+91  9876543210") is False, "Two spaces after +91 are not allowed: the separator is optional but single ([ -]?, not [ -]*)."
    assert is_mobile("919876543210") is False, "'91' without '+' is not a prefix. Did you make the '+' optional? Escape it as \\+ and require it."
    assert is_mobile("+92 9876543210") is False, "Only +91 is accepted."


def test_zero_prefix():
    assert is_mobile("09876543210") is True, "A single 0 directly before the number is allowed."
    assert is_mobile("0 9876543210") is False, "No space is allowed after the 0 prefix."
    assert is_mobile("009876543210") is False, "Only ONE 0 prefix."
    assert is_mobile("+91 09876543210") is False, "Only one prefix: +91 OR 0, not both. Use alternation (+91...|0) inside ONE optional group."


def test_middle_separator():
    assert is_mobile("98765 43210") is True, "One space between the 5th and 6th digit is allowed."
    assert is_mobile("98765-43210") is True, "One hyphen between the 5th and 6th digit is allowed."
    assert is_mobile("+91 98765-43210") is True, "Prefix separator and middle separator are independent."
    assert is_mobile("9876 543210") is False, "The middle separator is only allowed after the 5th digit: [6-9][0-9]{4}[ -]?[0-9]{5}."
    assert is_mobile("98765  43210") is False, "Only ONE separator in the middle."
    assert is_mobile("98765 - 43210") is False, "Space AND hyphen together is two separators: invalid."


def test_outer_whitespace_and_junk():
    assert is_mobile("  +919876543210 ") is True, "Spaces at the start and end are ignored: call s.strip() first."
    assert is_mobile("9876543210\n") is True, "A trailing newline is outer whitespace: strip() removes it."
    assert is_mobile("call 9876543210") is False, "Other text around the number is not allowed: use fullmatch, not search."
    assert is_mobile("(+91) 9876543210") is False, "Brackets are not allowed."
    assert is_mobile("") is False, "Empty input is not a number."


def test_ascii_digits_only():
    assert is_mobile("98765१२३४५") is False, "Only ASCII digits: \\d also matches Devanagari digits. Use [0-9]."


def test_returns_bool():
    assert type(is_mobile("9876543210")) is bool, "Return True/False, not a Match object."
    assert type(is_mobile("x")) is bool, "Return False, not None."
