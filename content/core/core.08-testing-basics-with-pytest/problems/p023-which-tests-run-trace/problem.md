# Which tests really run?

pytest collects functions whose names **start with `test`** (lower case, no underscore needed),
in the order they are defined in the file. A function can pass, fail, or be reported as an
`ERROR` when pytest cannot even set it up (for example, because the test function has a
parameter, which pytest treats as a request for a *fixture* named like the parameter, and no such
fixture exists). Python also keeps only the **last** definition when two functions share a name.

```python
import pytest


def double(n):
    return n * 2


def test_double():
    assert double(2) == 4


def test_double():
    assert double(3) == 7


def testtriple():
    assert double(1) == 2


def tests_helper():
    assert double(0) == 0


def Test_upper():
    assert double(1) == 2


def helper_test():
    assert False


def test_returns_nothing():
    double(5)


def test_error():
    raise RuntimeError("boom")


def test_extra_argument(n):
    assert n == 1


def test_last():
    assert double(-1) == -2
```

Predict `python -m pytest -v`. Write one line per collected test as `name PASSED`, `name FAILED`
or `name ERROR`, in the order pytest runs them, then the summary line exactly as pytest prints
it, for example `1 failed, 2 passed, 1 error`.
