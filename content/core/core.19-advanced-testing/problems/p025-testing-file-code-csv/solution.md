## Approach

Each bug lives in one row of a table of file contents, so a `parametrize` table is the natural shape:
every row is a tiny CSV and the dict you computed by hand. `tmp_path` makes the files, so nothing is
left behind and no test can see another test's data. The missing-file test uses a path inside
`tmp_path` that is never created.

## Code

```python
import pytest

from target import summarise


def write(tmp_path, text):
    path = tmp_path / "data.csv"
    path.write_text(text)
    return path


@pytest.mark.parametrize("text, expected", [
    ("category,amount\nfood,10\nfood,5\n", {"food": 15.0}),
    ("category,amount\nFood,1\nfood,2\n FOOD ,3\n", {"food": 6.0}),
    ("category,amount\nfood,\nrent,0\nfood, \n", {"rent": 0.0}),
    ("category,amount\nx,0.1\nx,0.2\n", {"x": 0.3}),
    ("category,amount\na,1\nb,2\na,3\n", {"a": 4.0, "b": 2.0}),
    ("category,amount\n", {}),
], ids=["sum", "case_and_strip", "blank_and_zero", "rounding", "two_categories", "header_only"])
def test_summarise(tmp_path, text, expected):
    assert summarise(write(tmp_path, text)) == expected


def test_amounts_are_summed_not_counted(tmp_path):
    assert summarise(write(tmp_path, "category,amount\nfood,2.5\nfood,2.5\nfood,2.5\n")) == {"food": 7.5}


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        summarise(tmp_path / "nope.csv")
```

## Complexity

Not applicable.

## Another way

Keep sample files in a `fixtures/` folder and copy them to `tmp_path`. Inline strings are better for
small cases because the input and the expected value sit next to each other.

## Notes

Windows: `write_text` may translate `\n` into `\r\n`; `csv` handles both.
