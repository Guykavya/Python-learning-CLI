import pandas as pd

from solution import parse_signup


def shown(dates):
    return [None if pd.isna(d) else d.strftime("%Y-%m-%d") for d in dates]


def run(values):
    return parse_signup(pd.Series(values))


def test_the_three_formats_give_the_same_date():
    dates, bad = run(["2024-03-05", "05/03/2024", "Mar 05, 2024"])
    assert shown(dates) == ["2024-03-05"] * 3, (
        "all three are 5 March 2024; the slash date is DAY first. Got %s." % shown(dates))
    assert bad == [], "nothing failed, so bad == []. Got %s." % bad


def test_day_first_for_slash_dates_only():
    dates, _ = run(["2024-03-05", "05/03/2024"])
    assert shown(dates)[0] == "2024-03-05", (
        "2024-03-05 is year-month-day. If you used dayfirst=True it became 2024-05-03.")
    assert shown(dates)[1] == "2024-03-05", "05/03/2024 is day/month/year = 5 March, not 3 May."


def test_unambiguous_day_above_twelve():
    dates, _ = run(["13/01/2024", "31/12/2023", "Dec 31, 2023"])
    assert shown(dates) == ["2024-01-13", "2023-12-31", "2023-12-31"], "got %s" % shown(dates)


def test_month_names():
    dates, _ = run(["Jan 01, 2024", "Feb 29, 2024", "Sep 09, 2024", "Dec 25, 2025"])
    assert shown(dates) == ["2024-01-01", "2024-02-29", "2024-09-09", "2025-12-25"], "got %s" % shown(dates)


def test_leap_day_only_in_leap_years():
    dates, bad = run(["29/02/2024", "29/02/2023"])
    assert shown(dates) == ["2024-02-29", None], "2024 is a leap year, 2023 is not. Got %s." % shown(dates)
    assert bad == ["29/02/2023"], "got %s" % bad


def test_impossible_dates_are_nat_and_listed():
    dates, bad = run(["31/04/2024", "2024-02-30", "2024-13-01", "00/01/2024", "2024-03-05"])
    assert shown(dates) == [None, None, None, None, "2024-03-05"], "impossible dates must be NaT. Got %s." % shown(dates)
    assert bad == ["00/01/2024", "2024-02-30", "2024-13-01", "31/04/2024"], (
        "bad = sorted distinct texts that could not be read. Got %s." % bad)


def test_text_matching_no_pattern_is_listed():
    dates, bad = run(["March 5", "5/3/24", "2024/03/05", "5 Mar 2024", "Mar 5, 2024", "tomorrow", ""])
    assert shown(dates) == [None] * 7, "none of these has one of the three shapes. Got %s." % shown(dates)
    assert bad == ["", "2024/03/05", "5 Mar 2024", "5/3/24", "Mar 5, 2024", "March 5", "tomorrow"], (
        "bad is sorted as text and also lists the empty text. Got %s." % bad)


def test_spaces_are_stripped_and_listed_stripped():
    dates, bad = run(["  05/03/2024 ", " 31/04/2024  "])
    assert shown(dates) == ["2024-03-05", None]
    assert bad == ["31/04/2024"], "list the STRIPPED text. Got %s." % bad


def test_only_full_matches_count():
    dates, bad = run(["2024-03-05 extra", "x05/03/2024"])
    assert shown(dates) == [None, None], "the whole text must match a pattern, not just its start."
    assert bad == ["2024-03-05 extra", "x05/03/2024"]


def test_missing_values_stay_nat_and_are_not_bad():
    dates, bad = run(["2024-03-05", None, float("nan")])
    assert shown(dates) == ["2024-03-05", None, None]
    assert bad == [], "missing input is not 'bad'. Got %s." % bad


def test_same_bad_text_listed_once_and_index_kept():
    s = pd.Series(["31/04/2024", "31/04/2024", "01/01/2024"], index=[5, 6, 7])
    dates, bad = parse_signup(s)
    assert bad == ["31/04/2024"], "each bad text appears once. Got %s." % bad
    assert dates.index.tolist() == [5, 6, 7], "keep the index of the input."
    assert pd.api.types.is_datetime64_any_dtype(dates), "return a datetime Series, not text. dtype is %s." % dates.dtype


def test_input_unchanged():
    s = pd.Series([" 05/03/2024", "bad"])
    parse_signup(s)
    assert s.tolist() == [" 05/03/2024", "bad"]
