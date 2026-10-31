# First properties: reverse and sort

An example test checks one input you chose. A **property** is a sentence that must be true for
**every** input, and hypothesis generates the inputs for you. Here is the code under test:

```python
def reverse(items):
    """Return a new list with the items in reverse order. The input is not changed."""
    return list(items[::-1])


def sorted_copy(items):
    """Return a new list with the same numbers in ascending order. The input is not changed."""
    return sorted(items)
```

In `solution.py` write **property tests** with `@given`. Import the code with
`from target import reverse, sorted_copy` (save it as `target.py` in your folder to try your tests).
Write at least 4 test functions. Put this above **every** `@given` test, so the run is repeatable and
leaves no `.hypothesis` folder:

```python
@settings(derandomize=True, database=None, max_examples=100)
```

Your tests must **pass** on the correct code and **fail** on each of six buggy versions. If a bug
survives, the report names it. Think about which sentence about `reverse` or `sorted_copy` the bug breaks.
One of the bugs is a trap: a test that only says "reverse twice gives the original" cannot see it.

**Example of one property test**

```python
from hypothesis import given, settings, strategies as st

@settings(derandomize=True, database=None, max_examples=100)
@given(st.lists(st.integers()))
def test_reverse_keeps_the_length(xs):
    assert len(reverse(xs)) == len(xs), "reverse must not add or drop elements."
```

**How this is checked.** Your `solution.py` is copied next to the code above (saved as `target.py`)
and real pytest runs on it: first on the correct code, then on each buggy copy. At least one of your
tests must fail on each bug.
