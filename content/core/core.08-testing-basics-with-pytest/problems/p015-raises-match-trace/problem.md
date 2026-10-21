# Which raises-tests pass?

`pytest.raises(E)` passes only if the block raises `E` (or a child of it). If nothing is raised,
the test fails with "DID NOT RAISE". If a **different** exception escapes, the test fails with that
exception. `match="text"` is a regular expression searched in the message, **not** a plain
substring (`+`, `.` and `(` have special meaning).

```python
import pytest


def parse_age(text):
    if not text.isdigit():
        raise ValueError("age must be digits, got " + repr(text))
    age = int(text)
    if age > 150:
        raise ValueError("age too large: " + text)
    return age


def test_a():
    with pytest.raises(ValueError):
        parse_age("abc")


def test_b():
    with pytest.raises(ValueError, match="digits"):
        parse_age("abc")


def test_c():
    with pytest.raises(ValueError, match="large"):
        parse_age("abc")


def test_d():
    with pytest.raises(TypeError):
        parse_age("abc")


def test_e():
    with pytest.raises(ValueError):
        parse_age("42")


def test_f():
    with pytest.raises(ValueError, match="age too large"):
        parse_age("200")


def test_g():
    with pytest.raises(Exception):
        parse_age(None)


def test_h():
    with pytest.raises(ValueError) as info:
        parse_age("x")
    assert "'x'" in str(info.value)


def test_i():
    with pytest.raises(ValueError, match="a+b"):
        parse_age("a+b")
```

Predict `python -m pytest -v`: one line per test, `test_x PASSED` or `test_x FAILED`, in file
order, then the summary line (`N failed, M passed`).
