# Testing file code: a CSV summariser

File code is easy to test **if** every test makes its own small file in a private temporary folder.
pytest's `tmp_path` fixture gives you that folder (a `pathlib.Path`) and deletes it later. Combine it
with `@pytest.mark.parametrize` to run one test body on many file contents.

```python
import csv


def summarise(path):
    """Read a CSV file with the header 'category,amount' and return {category: total}.
    Categories are stripped and lower-cased. Rows with a blank amount are skipped.
    Totals are rounded to 2 decimals. A missing file raises FileNotFoundError."""
    totals = {}
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            amount = row["amount"].strip()
            if not amount:
                continue
            category = row["category"].strip().lower()
            totals[category] = round(totals.get(category, 0) + float(amount), 2)
    return totals
```

Write tests (`from target import summarise`) that create CSV files with `tmp_path` and check: the sum
per category, the lower-casing and stripping of categories, blank amounts, a category whose amounts
are all zero, rounding of float sums, a file with only a header, and the missing file. Use `tmp_path`
and at least one `parametrize`. Write at least 3 test functions. Eight buggy versions are tried.

**Example**

```python
import pytest

@pytest.mark.parametrize("text, expected", [
    ("category,amount\nfood,10\nfood,5\n", {"food": 15.0}),
    ("category,amount\n", {}),
])
def test_totals(tmp_path, text, expected):
    path = tmp_path / "data.csv"
    path.write_text(text)
    assert summarise(path) == expected
```

**How this is checked.** Your `solution.py` is a file of pytest tests. The checker copies it next
to the code above (saved as `target.py`) and runs real pytest, first on the **correct** code (all
your tests must pass), then on several **buggy copies** (at least one of your tests must fail on
each; the report names any bug that survives). To try your tests yourself, save the code as
`target.py` in your folder and run `python -m pytest solution.py -p no:cacheprovider`.
