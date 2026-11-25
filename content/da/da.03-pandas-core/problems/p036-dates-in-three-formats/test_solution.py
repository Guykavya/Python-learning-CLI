from datetime import datetime

import pandas as pd

from solution import parse_dates

FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y"]


def slow(raw, formats):
    """The obvious loop: try each format with strptime, first match wins."""
    out, bad = [], []
    for text in raw:
        if text is None or pd.isna(text):
            out.append(None)
            continue
        for f in formats:
            try:
                out.append(datetime.strptime(text.strip(), f))
                break
            except ValueError:
                continue
        else:
            out.append(None)
            bad.append(text)
    return out, bad


def check(raw, formats, what):
    s = pd.Series(raw, index=range(100, 100 + len(raw)))
    before = s.tolist()
    got, bad = parse_dates(s, formats)
    assert isinstance(got, pd.Series) and str(got.dtype).startswith("datetime64"), (
        f"{what}: parsed must be a datetime Series, got {type(got).__name__} / {getattr(got, 'dtype', None)}.")
    assert got.index.tolist() == s.index.tolist(), f"{what}: keep the index of the input."
    want, want_bad = slow(raw, formats)
    for i, w in enumerate(want):
        have = got.iloc[i]
        if w is None:
            assert pd.isna(have), f"{what}: row {i} ({raw[i]!r}) should be NaT, got {have!r}."
        else:
            assert have == pd.Timestamp(w), f"{what}: row {i} ({raw[i]!r}) should be {w.date()}, got {have!r}."
    assert isinstance(bad, list), f"{what}: unparsed must be a list, got {type(bad).__name__}."
    assert bad == want_bad, f"{what}: unparsed should be {want_bad}, got {bad}. List raw texts that were not missing but matched no format."
    assert [None if pd.isna(x) else x for x in s.tolist()] == [None if pd.isna(x) else x for x in before], "do not change the input."


def test_the_example():
    raw = ["2025-03-01", "01/03/2025", "Mar 1, 2025", "31/02/2025", None, "13/02/2025"]
    check(raw, FORMATS, "example")
    parsed, bad = parse_dates(pd.Series(raw), FORMATS)
    assert bad == ["31/02/2025"], f"31 February does not exist: it must be reported, not guessed. Got {bad}."


def test_format_order_decides_ambiguous_text():
    s = pd.Series(["01/02/2024"])
    day_first, _ = parse_dates(s, ["%d/%m/%Y", "%m/%d/%Y"])
    month_first, _ = parse_dates(s, ["%m/%d/%Y", "%d/%m/%Y"])
    assert day_first.iloc[0] == pd.Timestamp("2024-02-01"), f"day-first order: expected 2024-02-01, got {day_first.iloc[0]}."
    assert month_first.iloc[0] == pd.Timestamp("2024-01-02"), f"month-first order: expected 2024-01-02, got {month_first.iloc[0]}."


def test_second_format_catches_what_the_first_cannot():
    s = pd.Series(["13/02/2024", "01/02/2024"])
    got, bad = parse_dates(s, ["%m/%d/%Y", "%d/%m/%Y"])
    assert got.tolist() == [pd.Timestamp("2024-02-13"), pd.Timestamp("2024-01-02")], (
        f"13 cannot be a month, so the second format must take over for that row only; got {got.tolist()}.")
    assert bad == [], f"nothing is unparsed here, got {bad}."


def test_spaces_missing_and_garbage():
    raw = ["  2025-01-31 ", "Jan 31, 2025", "", "not a date", "2025-13-01", "2025/01/31", None]
    check(raw, FORMATS, "spaces, empty, garbage")
    _, bad = parse_dates(pd.Series(raw), FORMATS)
    assert "" in bad, "an empty string is not missing (it is text) and matches no format: it belongs in unparsed."


def test_part_of_the_text_is_not_a_match():
    got, bad = parse_dates(pd.Series(["2025-03-01 10:30"]), ["%Y-%m-%d"])
    assert pd.isna(got.iloc[0]) and bad == ["2025-03-01 10:30"], (
        "a format must match the whole text: '2025-03-01 10:30' does not match '%Y-%m-%d'. "
        f"Got {got.tolist()} and {bad}.")


def test_many_random_rows_against_the_slow_loop():
    import random
    rnd = random.Random(36)
    raw = []
    for _ in range(300):
        d = datetime(2025, rnd.randint(1, 12), rnd.randint(1, 28))
        style = rnd.choice(["iso", "dmy", "mdy", "name", "bad", "none"])
        raw.append({"iso": d.strftime("%Y-%m-%d"), "dmy": d.strftime("%d/%m/%Y"), "mdy": d.strftime("%m/%d/%Y"),
                    "name": d.strftime("%b %d, %Y"), "bad": "??", "none": None}[style])
    check(raw, ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%b %d, %Y"], "300 random rows")
