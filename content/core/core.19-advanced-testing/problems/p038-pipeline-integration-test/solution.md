## Approach

One messy input file, chosen so that every rule changes the output, and one exact comparison of the output file:

```
d,Food,10.5      d, food ,4.5     -> food: 15.00, 2 rows   (case and spaces merge)
d,Rent,500                          -> rent: 500.00
d,Fun,           d,Fun,abc          -> dropped (blank, text)
d,Food,-3                           -> dropped (refund)
d,Games,15  (first row!)  d,Fun,15 -> games 15.00 and fun 15.00 tie with food: alphabetical, not input order
```

Expected report: `rent`, then `food`, `fun`, `games` (all 15.00, by name). Each bug changes a line of this file:
a missing header, an unsorted order, a wrong total, an extra row. The return value is checked against the **report** line count (4), not
the input row count (8), which catches the glue bug. `run_skips_clean` also shows up here, because without `clean` the messy file
would put ` food ` in its own category. The boundary files catch what the messy file cannot: with no rows at all the header must still appear.

## Code

```python
import csv

import pytest

from pipeline import run

HEADER = "date,category,amount\n"


def make_input(tmp_path, body):
    src = tmp_path / "in.csv"
    src.write_text(HEADER + body)
    return src, tmp_path / "out.csv"


def read_output(path):
    return path.read_text().splitlines()


def test_exact_report(tmp_path):
    src, dst = make_input(tmp_path, (
        "d,Games,15\n"
        "d,Food,10.5\n"
        "d, food ,4.5\n"
        "d,Rent,500\n"
        "d,Fun,\n"
        "d,Fun,abc\n"
        "d,Food,-3\n"
        "d,Fun,15\n"))
    written = run(src, dst)
    assert written == 4, "run must return the number of report lines, not the number of input rows."
    assert read_output(dst) == [
        "category,total,count",
        "rent,500.00,1",
        "food,15.00,2",
        "fun,15.00,1",
        "games,15.00,1",
    ], "Biggest total first; ties by name; totals with 2 decimals; blank, text and negative amounts dropped."


def test_header_only_file(tmp_path):
    src, dst = make_input(tmp_path, "")
    assert run(src, dst) == 0, "No data rows: nothing to report."
    assert read_output(dst) == ["category,total,count"], "The header is written even when there is no data."


def test_all_rows_invalid(tmp_path):
    src, dst = make_input(tmp_path, "d,Food,\nd,Food,-1\n")
    assert run(src, dst) == 0, "Every row is dropped, so the report has no data lines."
    assert read_output(dst) == ["category,total,count"]


def test_missing_input_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        run(tmp_path / "nope.csv", tmp_path / "out.csv")


def test_report_is_valid_csv_with_the_right_shape(tmp_path):
    src, dst = make_input(tmp_path, "d,a,1\nd,b,2.25\n")
    run(src, dst)
    with open(dst, newline="") as f:
        rows = list(csv.reader(f))
    assert rows == [["category", "total", "count"], ["b", "2.25", "1"], ["a", "1.00", "1"]], (
        "Two decimals and a count column.")
```

## Cost

Five tests, each writing two tiny files in a temporary folder: milliseconds.

## Another way

A **test data builder** (`make_input(tmp_path, rows)` taking a list of tuples) keeps the CSV text out of the tests. Or add one test
per rule that uses a two-row file: more tests, but a failure then points at one rule instead of the whole messy file.
