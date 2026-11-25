import random
import statistics

import pytest

from solution import describe, report


def test_every_number_against_statistics():
    rng = random.Random(11)
    data = [rng.gauss(100, 20) for _ in range(40)]
    messy = data[:10] + [None, None] + data[10:] + [None]
    d = describe(messy)
    q1, _, q3 = statistics.quantiles(data, n=4, method="inclusive")
    assert d["n"] == 40 and d["missing"] == 3, "n counts only real values; missing counts the Nones."
    assert d["mean"] == pytest.approx(statistics.fmean(data), rel=1e-9), "mean wrong (ignore the Nones)."
    assert d["median"] == pytest.approx(statistics.median(data), rel=1e-9), "median wrong."
    assert d["sd"] == pytest.approx(statistics.stdev(data), rel=1e-9), "sd must be the SAMPLE standard deviation."
    assert d["min"] == min(data) and d["max"] == max(data), "min or max wrong."
    assert d["q1"] == pytest.approx(q1, rel=1e-9) and d["q3"] == pytest.approx(q3, rel=1e-9), "Quartiles must use the inclusive method."
    assert d["iqr"] == pytest.approx(q3 - q1, rel=1e-9), "iqr = q3 - q1."
    want_hint = (statistics.fmean(data) - statistics.median(data)) / statistics.pstdev(data)
    assert d["skew_hint"] == pytest.approx(want_hint, rel=1e-9), "skew_hint = (mean - median) / POPULATION sd."
    assert set(d) == {"n", "missing", "mean", "median", "sd", "min", "q1", "q3", "max", "iqr", "skew_hint"}, "Return exactly the eleven documented keys."


def test_input_is_not_changed():
    data = [3, None, 1, 2]
    describe(data)
    assert data == [3, None, 1, 2], "Do not modify the caller's list."


def test_single_value():
    d = describe([7, None])
    assert d["n"] == 1 and d["missing"] == 1, "One real value, one missing."
    assert d["sd"] is None, "A single value has no sample sd: None."
    assert d["q1"] == 7 and d["q3"] == 7 and d["iqr"] == 0, "With one value, q1 = q3 = the value."
    assert d["skew_hint"] == 0.0, "No spread: skew_hint is 0.0, not a ZeroDivisionError."


def test_constant_list():
    d = describe([5, 5, 5])
    assert d["sd"] == 0 and d["skew_hint"] == 0.0, "Constant data: sd 0 and skew_hint 0.0."


def test_nothing_to_describe():
    for data in ([], [None, None]):
        with pytest.raises(ValueError):
            describe(data)


EXAMPLE = [10, 15, 20, 25, 100, None]


def test_report_example_exactly():
    got = report("Response time", EXAMPLE, "ms")
    want = "\n".join([
        "Response time  (n = 5, missing = 1)",
        "-" * 40,
        "centre : mean 34.0 ms   median 20.0 ms",
        "spread : sd " + f"{statistics.stdev([10, 15, 20, 25, 100]):.1f}" + "   IQR 10.0",
        "range  : 10.0 to 100.0",
        "advice : report the median (the mean and the median differ by more than 10%)",
    ])
    assert got == want, "The report must match the six-line format of the statement exactly.\nGot:\n" + got


def test_report_without_unit_and_symmetric_advice():
    got = report("Marks", [48, 49, 50, 51, 52]).split("\n")
    assert got[0] == "Marks  (n = 5, missing = 0)", "First line: name, two spaces, (n = .., missing = ..)."
    assert got[2] == "centre : mean 50.0   median 50.0", "Without a unit there is no trailing text after the numbers."
    assert got[5] == "advice : either centre is fine", "Mean and median agree: either centre is fine."
    assert len(got) == 6, "Exactly six lines."


def test_advice_follows_the_ten_percent_rule():
    skewed = [10, 11, 12, 13, 14, 15, 200]
    assert report("x", skewed).endswith("report the median (the mean and the median differ by more than 10%)"), "A mean far above the median: advise the median."
    close = [100, 101, 102, 103, 110]
    assert report("x", close).split("\n")[5] == "advice : either centre is fine", "mean 103.2 vs median 102: within 10%, so either centre is fine."


def test_report_one_value_shows_na():
    line = report("One", [4.0]).split("\n")[3]
    assert line == "spread : sd n/a   IQR 0.0", "With a single value the sd is None: print n/a."
