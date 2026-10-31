from solution import find_dates


def test_example():
    got = find_dates("Paid on 5/3/2024, due 2024-04-01. Not a date: 13/13/2024")
    assert got == ["2024-03-05", "2024-04-01"], f"Find both forms in order, pad to two digits, skip month 13. Got {got!r}."


def test_indian_style_day_first():
    assert find_dates("05/03/2024") == ["2024-03-05"], "Day comes FIRST in d/m/yyyy: 05/03/2024 is 5 March, so 2024-03-05."
    assert find_dates("31/12/2023") == ["2023-12-31"], "Reorder to year-month-day."


def test_padding():
    assert find_dates("1/2/2024") == ["2024-02-01"], "Pad day and month to two digits: f'{n:02d}'."


def test_iso_style():
    assert find_dates("released 2024-03-05.") == ["2024-03-05"], "An ISO date is returned as it is."
    assert find_dates("2024-3-5") == [], "ISO style needs exactly two digits for month and day: '2024-3-5' is not a date here."


def test_order_and_duplicates():
    got = find_dates("2024-01-02 and 3/4/2023 and 2024-01-02")
    assert got == ["2024-01-02", "2023-04-03", "2024-01-02"], "Keep text order and keep repeats. Do not sort or de-duplicate, and do not collect one format before the other."


def test_range_checks():
    assert find_dates("13/13/2024") == [], "Month 13 is invalid: skip it."
    assert find_dates("00/10/2024") == [], "Day 0 is invalid."
    assert find_dates("32/01/2024") == [], "Day 32 is invalid."
    assert find_dates("2024-00-10 2024-12-32") == [], "ISO dates are range-checked too."
    assert find_dates("31/02/2024") == ["2024-02-31"], "No days-per-month check is required: day 31 is within 1-31."


def test_not_glued():
    assert find_dates("x12/05/2024") == [], "A letter glued to the front: not a date. Put \\b at the start."
    assert find_dates("12/05/20245") == [], "A 5-digit year: not a date. Put \\b at the end; otherwise '12/05/2024' is found inside."
    assert find_dates("112/05/2024") == [], "'112/05/2024' must not yield '12/05/2024': \\b before the day stops a match from starting mid-number."
    assert find_dates("2024-03-055") == [], "Extra digit after the day: not a date."
    assert find_dates("id_2024-03-05") == [], "Underscore is a word character, so the date is glued to 'id_'."


def test_punctuation_around():
    got = find_dates("(5/3/2024), [2024-03-06]; '7/3/2024'")
    assert got == ["2024-03-05", "2024-03-06", "2024-03-07"], f"Brackets, commas and quotes around a date are fine, and the result keeps text order (one scan for both forms). Got {got!r}."


def test_none():
    assert find_dates("") == [], "Empty text: no dates."
    assert find_dates("version 1.2.3 on 12-05-2024 or 2024/05/12") == [], "Mixed separators are neither form: dd-mm-yyyy and yyyy/mm/dd do not count."
