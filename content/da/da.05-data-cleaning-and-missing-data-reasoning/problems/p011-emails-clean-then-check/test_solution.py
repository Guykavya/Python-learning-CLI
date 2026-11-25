import pandas as pd

from solution import clean_email

CASES = [
    ("Asha@Example.COM ", "asha@example.com"),
    ("dev.k+x@sub.mail.example", "dev.k+x@sub.mail.example"),
    ("user_name@mail.example", "user_name@mail.example"),
    ("MEERA1002@MAIL.EXAMPLE", "meera1002@mail.example"),
    ("  nina1003@mail.example  ", "nina1003@mail.example"),
    ("a-b@x-y.co", "a-b@x-y.co"),
    ("meera1042mail.example", None),
    ("a@b", None),
    ("a@x..com", None),
    ("a@x.com.", None),
    ("@x.com", None),
    ("a@@x.com", None),
    ("a@b@x.com", None),
    ("a b@x.com", None),
    ("a@x.com extra", None),
    ("a@.com", None),
    ("", None),
]


def one(text):
    return clean_email(pd.Series([text])).iloc[0]


def check(cases):
    for text, want in cases:
        got = one(text)
        if want is None:
            assert pd.isna(got), "%r does not look like an email: expected missing, got %r." % (text, got)
        else:
            assert not pd.isna(got), "%r is a fine address (after cleaning): expected %r, got missing." % (text, want)
            assert got == want, "%r should give %r, got %r." % (text, want, got)


def test_clean_before_check_upper_case_and_spaces():
    check(CASES[:5])


def test_allowed_characters():
    check(CASES[1:3] + CASES[5:6])


def test_no_at_sign_and_no_dot_in_domain():
    check(CASES[6:8])


def test_empty_parts_are_rejected():
    check(CASES[8:11] + CASES[15:16])


def test_two_at_signs_spaces_and_extra_text_are_rejected():
    check(CASES[11:15])
    assert pd.isna(one("x@y.com\nz@y.com")), "the whole text must be one address; use fullmatch, not match or contains."


def test_empty_text_is_missing():
    check(CASES[16:])


def test_missing_stays_missing_without_error():
    out = clean_email(pd.Series(["a@x.com", None, float("nan")]))
    assert out.isna().tolist() == [False, True, True], "got %s" % out.tolist()


def test_whole_column_index_and_input_unchanged():
    texts = [c[0] for c in CASES]
    s = pd.Series(texts, index=range(50, 50 + len(texts)))
    out = clean_email(s)
    assert out.index.tolist() == s.index.tolist()
    assert [None if pd.isna(v) else v for v in out.tolist()] == [c[1] for c in CASES]
    assert s.tolist() == texts, "do not change the input."
