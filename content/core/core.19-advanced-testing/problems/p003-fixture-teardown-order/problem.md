# Trace: fixture teardown order

A fixture with `yield` runs everything **before** the `yield` as setup and everything **after**
it as teardown, once the test is finished (pass **or** fail). A fixture that needs another
fixture (like `session` needs `db`) is set up **after** it and torn down **before** it.

This file runs its own tests with `pytest.main`. What does it print?

Save it as `demo.py` and run `python demo.py` to check yourself. The line `-p no:terminal` turns
off pytest's own report, and `-s` lets `print` show immediately, so the only output is the
program's `print` lines. A failing test is not an error here: it is part of the story.

```python
import pytest


@pytest.fixture
def db():
    print("open db")
    yield "db"
    print("close db")


@pytest.fixture
def session(db):
    print("start session")
    yield "session"
    print("end session")


@pytest.fixture
def cache():
    print("fill cache")
    yield []
    print("clear cache")


def test_one(session, cache):
    print("test_one runs")


def test_two(cache):
    print("test_two runs")
    assert 1 == 2, "this test fails"


if __name__ == "__main__":
    code = pytest.main([__file__, "-s", "-p", "no:terminal", "-p", "no:cacheprovider"])
    print("pytest exit code", int(code))
```

Write in `answer.txt` the lines the program prints, in order, one per line.
