# Idempotence and invariants

Two more families of properties:

- **Idempotent**: doing it twice is the same as doing it once, `f(f(x)) == f(x)`.
- **Invariant**: something stays true about the output (no duplicates, length unchanged, order kept).

Here is the code under test:

```python
def normalise_whitespace(text):
    """Collapse every run of whitespace (spaces, tabs, newlines) into one space and strip both ends."""
    return " ".join(text.split())


def dedupe(items):
    """Remove repeated items. Keep the FIRST occurrence of each and the original order."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def sort_by_length(words):
    """Return a new list ordered by length, shortest first. Words of equal length keep their original order."""
    return sorted(words, key=len)
```

In `solution.py` write property tests (`from target import normalise_whitespace, dedupe, sort_by_length`; save the code above as
`target.py` to try them). Write at least 5 test functions. Put
`@settings(derandomize=True, database=None, max_examples=100)` above every `@given`.

Your tests must **pass** on the correct code and **fail** on each of nine buggy versions. The report names the survivors.

Hints about strategies: to test whitespace you must generate whitespace, so give `st.text` an `alphabet` such as
`" \t\nab"`. To test order and duplicates, use small values (`st.integers(0, 6)`) so repeats are common. To test stability, use
short words from a small alphabet so that many words have the same length.

**Example**

```python
@settings(derandomize=True, database=None, max_examples=100)
@given(st.text(alphabet=" \t\nab", max_size=25))
def test_normalise_is_idempotent(text):
    once = normalise_whitespace(text)
    assert normalise_whitespace(once) == once, "Normalising twice must equal normalising once."
```

**How this is checked.** Your `solution.py` is copied next to the code above (saved as `target.py`)
and real pytest runs on it: first on the correct code, then on each buggy copy. At least one test must fail on each bug.
