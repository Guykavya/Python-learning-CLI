import pytest

from solution import load_column

MESSY = """id,endpoint,ms
1,/home,120.5
2,/home, 98ms
3,/search,"1,204"
4,/search,
5,/home,N/A
6,/cart,-5
7,/cart,131
7,/cart,131
8,/cart,abc
9,/cart,99999
"""


@pytest.fixture
def messy(tmp_path):
    path = tmp_path / "messy.csv"
    path.write_text(MESSY, encoding="utf-8", newline="")
    return str(path)


def test_everything_at_once(messy):
    values, report = load_column(messy, "ms", low=0, high=5000, dedupe_on=["id"])
    assert values == [120.5, 98.0, 1204.0, 131.0], f"Kept values wrong: {values}. Keep file order; '1,204' is 1204 and ' 98ms ' is 98."
    assert report == {"missing": 2, "unparseable": 1, "out_of_range": 2, "duplicate": 1}, f"Report wrong: {report}."


def test_no_range_and_no_dedupe(messy):
    values, report = load_column(messy, "ms")
    assert -5.0 in values and 99999.0 in values, "Without low/high nothing is out of range."
    assert report["out_of_range"] == 0 and report["duplicate"] == 0, "Without dedupe_on nothing is a duplicate."
    assert values.count(131.0) == 2, "Without dedupe_on both copies of row 7 stay."


def test_report_always_has_four_keys(messy):
    _, report = load_column(messy, "id")
    assert set(report) == {"missing", "unparseable", "out_of_range", "duplicate"}, "Always return all four keys, even when a count is 0."
    assert report == {"missing": 0, "unparseable": 0, "out_of_range": 0, "duplicate": 0}, "The id column is clean."


def test_every_row_lands_in_exactly_one_bucket(messy):
    values, report = load_column(messy, "ms", low=0, high=5000, dedupe_on=["id"])
    assert len(values) + sum(report.values()) == 10, "Each of the 10 data rows is kept or counted once."


def test_duplicate_is_checked_before_parsing(tmp_path):
    path = tmp_path / "d.csv"
    path.write_text("id,v\n1,abc\n1,abc\n", encoding="utf-8", newline="")
    values, report = load_column(str(path), "v", dedupe_on=["id"])
    assert report == {"missing": 0, "unparseable": 1, "out_of_range": 0, "duplicate": 1}, f"Check duplicates first: the second 'abc' row is a duplicate, not a second unparseable row. Got {report}"


def test_missing_column(messy):
    with pytest.raises(KeyError, match="latency"):
        load_column(messy, "latency")
    with pytest.raises(KeyError, match="user"):
        load_column(messy, "ms", dedupe_on=["user"])


def test_bounds_are_inclusive(tmp_path):
    path = tmp_path / "b.csv"
    path.write_text("v\n0\n10\n-0.1\n10.1\n", encoding="utf-8", newline="")
    values, report = load_column(str(path), "v", low=0, high=10)
    assert values == [0.0, 10.0], "low and high themselves are kept (inclusive range)."
    assert report["out_of_range"] == 2, "-0.1 and 10.1 are out of range."


def test_utf8_and_quoted_newline(tmp_path):
    path = tmp_path / "u.csv"
    path.write_bytes('name,v\n"caf\u00e9\nbar",5\nx,6\n'.encode("utf-8"))
    values, _ = load_column(str(path), "v")
    assert values == [5.0, 6.0], "Open with newline='' and encoding='utf-8' so quoted line breaks and accents work."


def test_empty_file_with_header(tmp_path):
    path = tmp_path / "e.csv"
    path.write_text("v\n", encoding="utf-8")
    assert load_column(str(path), "v") == ([], {"missing": 0, "unparseable": 0, "out_of_range": 0, "duplicate": 0}), "A header only file gives no values and an all-zero report."
