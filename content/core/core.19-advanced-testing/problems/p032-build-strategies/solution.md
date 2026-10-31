## Approach

Translate each description word by word into the matching strategy and its limits:

- "whole numbers from 1 to 100" is `st.integers(min_value=1, max_value=100)`.
- "lowercase ASCII letters" is an `alphabet`. `string.ascii_lowercase` is exactly `a`..`z`; `st.text()` alone would give any Unicode character.
- A list of digits is `lists(integers(0, 9), min_size=1, max_size=5)`: the element strategy inside the list strategy.
- A dictionary needs a strategy for the keys and one for the values. With both `min_value` and `max_value`, `st.floats` excludes `nan` and infinity by itself.
- `st.builds(Point, ...)` is the way to generate your own classes.
- "this or that" is `st.one_of(...)`; a fixed list of choices is `st.sampled_from(...)`.

## Code

```python
import string
from dataclasses import dataclass

from hypothesis import strategies as st

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


@dataclass(frozen=True)
class Point:
    x: int
    y: int


small_ints = st.integers(min_value=1, max_value=100)
usernames = st.text(alphabet=string.ascii_lowercase, min_size=3, max_size=12)
digit_lists = st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=5)
stock = st.dictionaries(
    st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=5),
    st.floats(min_value=0, max_value=100),
    min_size=1,
    max_size=4,
)
points = st.builds(Point, x=st.integers(-10, 10), y=st.integers(-10, 10))
id_or_none = st.one_of(st.none(), st.integers(min_value=1, max_value=999))
weekdays = st.sampled_from(DAYS)
```

## Cost

Strategies are lazy descriptions: nothing is generated until a test runs. Building them costs nothing.

## Another way

`st.integers(1, 999) | st.none()` (the `|` operator) is the same as `one_of`. `st.from_type(Point)` builds a `Point` from its type hints (`int` fields, unbounded), so use `builds` when you need limits. For
`weekdays` you can also write `st.sampled_from(["mon", "tue", ...])` directly with a literal list.
