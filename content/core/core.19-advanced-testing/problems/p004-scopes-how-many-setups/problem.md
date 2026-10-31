# Trace: how many times does setup run?

A fixture's **scope** says how long its value lives. The default is `"function"`: one new value
per test. `scope="module"` builds the value once for the whole file, on first use, and tears it
down after the last test of the file.

Trace the counters and the order of the prints.

Save it as `demo.py` and run `python demo.py` to check yourself. The line `-p no:terminal` turns
off pytest's own report, and `-s` lets `print` show immediately, so the only output is the
program's `print` lines. A failing test is not an error here: it is part of the story.

```python
import pytest

calls = {"function": 0, "module": 0}


@pytest.fixture
def per_test():
    calls["function"] += 1
    print("per_test setup", calls["function"])
    return calls["function"]


@pytest.fixture(scope="module")
def per_module():
    calls["module"] += 1
    print("per_module setup", calls["module"])
    yield calls["module"]
    print("per_module teardown")


def test_a(per_test, per_module):
    print("a:", per_test, per_module)


def test_b(per_test, per_module):
    print("b:", per_test, per_module)


def test_c(per_module):
    print("c:", per_module)


def test_d(per_test):
    print("d:", per_test)


if __name__ == "__main__":
    code = pytest.main([__file__, "-s", "-p", "no:terminal", "-p", "no:cacheprovider"])
    print("pytest exit code", int(code))
```

Write in `answer.txt` the lines the program prints, in order, one per line.
