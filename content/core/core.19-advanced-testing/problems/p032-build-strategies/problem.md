# Build strategies for data shapes

A hypothesis test is only as good as its strategy: it must generate the data your function accepts, and enough variety to find bugs. The default
`st.integers()` gives numbers up to 2^64 and `st.text()` gives any Unicode character, which is rarely what a real function takes.

In `solution.py`, define these **module-level variables**, each a strategy (the starter already has the `Point` class and a lax first version of each):

| Name | Must generate |
|---|---|
| `small_ints` | whole numbers from 1 to 100, inclusive |
| `usernames` | text of 3 to 12 lowercase ASCII letters (`a`-`z`), nothing else |
| `digit_lists` | lists of 1 to 5 whole numbers, each from 0 to 9 |
| `stock` | dictionaries with 1 to 4 entries: key = 1 to 5 lowercase letters, value = a float from 0 to 100 (no `nan`, no infinity) |
| `points` | `Point(x, y)` objects (the class is in the starter) with `x` and `y` whole numbers from -10 to 10 |
| `id_or_none` | either `None` or a whole number from 1 to 999 |
| `weekdays` | one of `"mon"`, `"tue"`, `"wed"`, `"thu"`, `"fri"`, `"sat"`, `"sun"` |

Tools (chapter section 12): `st.integers(min_value, max_value)`, `st.text(alphabet=..., min_size=..., max_size=...)`,
`st.lists(elements, min_size=..., max_size=...)`, `st.dictionaries(keys, values, min_size=..., max_size=...)`, `st.floats(min_value, max_value)`,
`st.builds(Class, field=strategy, ...)`, `st.one_of(a, b)`, `st.none()`, `st.sampled_from(list)`.

**How this is checked.** For each name the checker draws 100 examples (the same ones every run:
`@settings(derandomize=True, database=None, max_examples=100)`), then verifies that every example has the right shape
and that the examples show real variety (both ends of a range, short and long, both `None` and numbers). The report shows
the offending examples.

**Example**

```python
small_odds = st.integers(min_value=1, max_value=99).map(lambda n: n * 2 - 1)   # not required here, just the idea
```
