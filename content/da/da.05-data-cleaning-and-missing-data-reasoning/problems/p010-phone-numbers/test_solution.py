import pandas as pd

from solution import clean_phone

# (input, expected output or None for missing)
CASES = [
    ("9876543210", "9876543210"),
    ("98765 43210", "9876543210"),
    ("+91-98765-43210", "9876543210"),
    ("(+91) 9876543210", "9876543210"),
    ("098765-43210", "9876543210"),
    ("919876543210", "9876543210"),
    ("9123456789", "9123456789"),
    ("06876543210", "6876543210"),
    ("phone: 98765-43210", "9876543210"),
    ("5876543210", None),
    ("91234", None),
    ("7874273", None),
    ("0919876543210", None),
    ("00919876543210", None),
    ("n/a", None),
    ("", None),
    ("1234567890", None),
]


def one(text):
    return clean_phone(pd.Series([text])).iloc[0]


def check(cases):
    for text, want in cases:
        got = one(text)
        if want is None:
            assert pd.isna(got), "%r is not a valid mobile number: expected missing, got %r." % (text, got)
        else:
            assert not pd.isna(got), "%r should give %r but you returned missing." % (text, want)
            assert got == want, "%r should give %r, got %r." % (text, want, got)


def test_decoration_is_removed():
    check(CASES[:5])


def test_country_code_and_trunk_zero_when_ten_digits_follow():
    check(CASES[5:6] + CASES[7:8])


def test_a_real_number_that_starts_with_91_is_not_cut():
    check([CASES[6]])
    assert one("9112345678") == "9112345678", "9112345678 is a 10-digit number starting with 91: keep all of it."


def test_other_text_around_the_digits():
    check(CASES[8:9])


def test_invalid_numbers_become_missing():
    check(CASES[9:])


def test_prefix_is_removed_only_once():
    assert pd.isna(one("0919876543210")), "0 + 91 + 10 digits is 13 digits: only ONE prefix may be removed, so it is invalid."
    assert pd.isna(one("919876543210" + "1")), "91 + 11 digits: after removing 91 there are 11 digits, still invalid."


def test_missing_input_stays_missing_and_no_error():
    out = clean_phone(pd.Series(["9876543210", None, float("nan")]))
    assert out.isna().tolist() == [False, True, True], "missing in, missing out. Got %s." % out.tolist()


def test_whole_column_and_index():
    texts = [c[0] for c in CASES]
    s = pd.Series(texts, index=range(100, 100 + len(texts)))
    out = clean_phone(s)
    assert out.index.tolist() == s.index.tolist(), "keep the index of the input."
    assert [None if pd.isna(v) else v for v in out.tolist()] == [c[1] for c in CASES]
    assert s.tolist() == texts, "do not change the input."
    assert int(out.notna().sum()) == sum(1 for c in CASES if c[1] is not None)


def test_result_is_text_not_numbers():
    out = clean_phone(pd.Series(["+91 98765 43210"]))
    assert isinstance(out.iloc[0], str), "return the number as TEXT; a 10-digit phone is a label, not a quantity."
