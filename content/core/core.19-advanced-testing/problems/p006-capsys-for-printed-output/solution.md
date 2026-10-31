## Approach

Capture, then compare the **exact text**. Comparing whole strings (or `splitlines()` lists) is
stricter than `"tea" in out`, which almost any buggy version would still satisfy. Choose inputs
that separate the correct behaviour from each bug: names out of alphabetical order with amounts
out of numeric order, amounts that need padding to two decimals, an empty list.

## Code

```python
from target import print_report


def test_one_sale_exact_text(capsys):
    print_report([("tea", 2.5)])
    assert capsys.readouterr().out == "tea: 2.50\nTOTAL: 2.50\n"


def test_lines_are_sorted_by_name(capsys):
    print_report([("tea", 1.0), ("cake", 9.0), ("apple", 5.0)])
    assert capsys.readouterr().out.splitlines()[:3] == ["apple: 5.00", "cake: 9.00", "tea: 1.00"]


def test_total_is_the_sum(capsys):
    print_report([("a", 1.25), ("b", 2.5), ("c", 4)])
    assert capsys.readouterr().out.splitlines()[-1] == "TOTAL: 7.75"


def test_empty_report(capsys):
    print_report([])
    assert capsys.readouterr().out == "No sales\n"


def test_nothing_on_stderr(capsys):
    print_report([("a", 1)])
    assert capsys.readouterr().err == ""
```

## Cost

Capturing costs nothing noticeable. Note that `readouterr()` **empties** the buffer: a second
call sees only what was printed after the first.

## Another way

`capfd` captures at the file-descriptor level (needed for output from C code or subprocesses).
Better design: make `print_report` **return** the text (or take a `file=` argument) and test
that with no capture at all.
