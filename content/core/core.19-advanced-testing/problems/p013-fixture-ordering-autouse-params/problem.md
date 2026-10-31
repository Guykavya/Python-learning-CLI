# Trace: autouse fixtures and parameters

Three ideas meet in this file:

- an **autouse** fixture runs for every test in its scope without being named;
- a fixture with `params=[...]` makes every test that uses it run **once per parameter**;
- when a **module-scoped** fixture is parametrized, pytest **reorders** the tests so that all
  tests for one parameter run together (so the expensive fixture is built as few times as
  possible).

Work out the exact output. This is the hardest trace of the module: take your time, write the
list of tests pytest will run (with their parameters) first.

Save it as `demo.py` and run `python demo.py` to check yourself. The line `-p no:terminal` turns
off pytest's own report, and `-s` lets `print` show immediately, so the only output is the
program's `print` lines. A failing test is not an error here: it is part of the story.

```python
import pytest


@pytest.fixture(scope="module", autouse=True)
def banner():
    print("module autouse up")
    yield
    print("module autouse down")


@pytest.fixture(autouse=True)
def tick():
    print("  tick up")
    yield
    print("  tick down")


@pytest.fixture(scope="module", params=["x", "y"])
def letter(request):
    print("  letter", request.param, "up")
    yield request.param
    print("  letter", request.param, "down")


@pytest.fixture
def number(letter):
    print("  number for", letter)
    return 1


def test_plain():
    print("  test_plain")


def test_letter(letter):
    print("  test_letter", letter)


@pytest.mark.parametrize("n", [1, 2])
def test_number(number, n):
    print("  test_number", n)


if __name__ == "__main__":
    code = pytest.main([__file__, "-s", "-p", "no:terminal", "-p", "no:cacheprovider"])
    print("pytest exit code", int(code))
```

Write in `answer.txt` the lines the program prints, in order, one per line.
