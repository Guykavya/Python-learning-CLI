# Which tests pass?

Here is a whole test file, `test_add.py`. Predict what `python -m pytest -v` reports.

```python
def add(a, b):
    return a + b


def test_add_small():
    assert add(2, 3) == 5


def test_add_negative():
    assert add(-1, 1) == 1


def test_add_zero():
    assert add(0, 0) == 0


def check_add_big():
    assert add(10**6, 1) == 0


def test_add_float():
    assert add(0.5, 0.25) == 0.75


def test_add_strings():
    assert add("a", "b") == "ab"


def test_add_mixed():
    assert add("1", 1) == 2
```

Write one line for every test pytest **collects**, in the order pytest runs them (the order in the
file), in the form `test_name PASSED` or `test_name FAILED`. Then add a last line with the summary,
in the exact style pytest uses, for example `1 failed, 4 passed` (pytest lists `failed` before
`passed`).

Careful: not every function in the file is a test.

Write your answer in `answer.txt`.
