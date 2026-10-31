from solution import numbers


def test_basic():
    assert numbers("Room 101, floor -2, 3 lifts") == [101, -2, 3], "Find every run of digits, in order. '-2' has a minus directly before it: make the minus optional with -?."


def test_returns_ints():
    result = numbers("a 12 b 5")
    assert result == [12, 5], "Two numbers: 12 and 5."
    assert all(type(x) is int for x in result), "Convert each match with int(): findall gives strings like '12'."


def test_multi_digit_runs():
    assert numbers("1234") == [1234], "Use + (one or more) so the whole run of digits is one number, not [1, 2, 3, 4]."
    assert numbers("x9y88z777") == [9, 88, 777], "Numbers glued to letters still count; each run of digits is one number."


def test_leading_zeros():
    assert numbers("007 agents") == [7], "int('007') is 7."


def test_negative_rules():
    assert numbers("temp -5 and - 6") == [-5, 6], "'-5' is negative. In '- 6' the minus is not directly before the digit, so it is just 6."
    assert numbers("10-3") == [10, -3], "The rule is simple: a minus directly before digits is a sign. '10-3' gives 10 and -3."
    assert numbers("--4") == [-4], "Only ONE optional minus is part of the number: '--4' gives -4."
    assert numbers("-") == [], "A lone minus is not a number. The digits part needs + (at least one digit)."


def test_decimal_point_is_separator():
    assert numbers("pi is about 3.14") == [3, 14], "Only integers: the dot separates 3 and 14."


def test_no_numbers():
    assert numbers("no digits here") == [], "No digits: return an empty list."
    assert numbers("") == [], "Empty text: return an empty list."
