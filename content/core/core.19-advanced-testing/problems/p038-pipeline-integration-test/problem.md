# An integration test across a pipeline

Unit tests check each function alone. An **integration test** runs several pieces together, here a whole
pipeline over a real file: read, clean, aggregate, write.

```python
import csv


def read_rows(path):
    """Read a CSV file with the header date,category,amount. Return a list of dicts of strings."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clean(rows):
    """Tidy the rows. Category: strip spaces, lower-case. Amount: text -> float.

    Drop a row when its amount is blank, not a number, or negative (refunds are ignored).
    """
    cleaned = []
    for row in rows:
        category = row["category"].strip().lower()
        try:
            amount = float(row["amount"])
        except ValueError:
            continue
        if amount < 0:
            continue
        cleaned.append({"category": category, "amount": amount})
    return cleaned


def aggregate(rows):
    """Return {category: (total, count)} for cleaned rows."""
    totals = {}
    for row in rows:
        total, count = totals.get(row["category"], (0.0, 0))
        totals[row["category"]] = (total + row["amount"], count + 1)
    return totals


def write_report(summary, path):
    """Write category,total,count lines: biggest total first, ties by category name.

    Totals have 2 decimals. The header line is always written. Return the number of data lines.
    """
    ordered = sorted(summary.items(), key=lambda item: (-item[1][0], item[0]))
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "total", "count"])
        for category, (total, count) in ordered:
            writer.writerow([category, f"{total:.2f}", count])
    return len(ordered)


def run(src, dst):
    """The whole pipeline: read src, clean, aggregate, write dst. Return the number of report lines."""
    return write_report(aggregate(clean(read_rows(src))), dst)
```

In `solution.py` write tests for `run(src, dst)` (`from pipeline import run`; save the code above as `pipeline.py` to try your tests). Use the
`tmp_path` fixture: write an input CSV into it, call `run`, read the report back. Write at least 5 test functions.

Your tests must **pass** on the correct code and **fail** on each of ten buggy versions. Some bugs are inside one step. Two are in the **glue**
(`run` itself): each step works, but `run` forgets one or reports the wrong number. The report names the survivors.

Think about:

- one **messy file** that exercises every rule at once (mixed case, spaces, blank, text and negative amounts, ties);
- the **boundaries**: a file with only the header, a file where every row is dropped, a missing input file;
- checking the **whole output file**, line by line, not one number.

**Example**

```python
def test_simple_file(tmp_path):
    src = tmp_path / "in.csv"
    src.write_text("date,category,amount\n2025-01-01,food,10\n")
    dst = tmp_path / "out.csv"
    assert run(src, dst) == 1, "one category, so one report line."
    assert dst.read_text().splitlines() == ["category,total,count", "food,10.00,1"]
```

**How this is checked.** Your `solution.py` is copied next to the code above (saved as `pipeline.py`)
and real pytest runs on it: first on the correct code, then on each buggy copy. At least one test must fail on each bug.
