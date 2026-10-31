## Approach

Turn every rule into a **free choice plus a transformation** that keeps the result valid:

- even = 2 times any integer, so choose from -500..500 and double: exactly the evens from -1000 to 1000, none rejected;
- sorted = sort any list: sorting preserves length and elements and makes the order valid;
- an ordered pair: pick `a`, pick a positive gap, and `b = a + gap` is bigger than `a` by construction;
- a multiple of 1000 in range: -1000..1000 times 1000. The filtered version keeps one example in 1000 and fails hypothesis' health check;
- distinct values: `unique=True` is a built-in constructive option.

## Code

```python
from hypothesis import strategies as st

even_numbers = st.integers(min_value=-500, max_value=500).map(lambda n: n * 2)
sorted_lists = st.lists(st.integers(min_value=-50, max_value=50), max_size=10).map(sorted)
ordered_pairs = st.tuples(st.integers(-100, 100), st.integers(1, 50)).map(lambda t: (t[0], t[0] + t[1]))
multiples_of_1000 = st.integers(min_value=-1000, max_value=1000).map(lambda n: n * 1000)
distinct_lists = st.lists(st.integers(min_value=-20, max_value=20), min_size=2, max_size=8, unique=True)
```

## Cost

Constructed strategies use every example hypothesis generates. A filter that keeps 1 in 1000 does a thousand times more work for the same number of usable
examples, and past a limit hypothesis stops with a `FailedHealthCheck`. Also, shrinking works better on constructed values: it can shrink the free choice (the `n` in `n * 2`).

## Another way

`st.integers().filter(...)` is fine when the filter rejects very little (say `n != 0`). When the relation between values is complicated (a list and a valid
index into it), use `st.data()` or `@st.composite` to draw step by step, or `.flatmap`. `assume(...)` inside a test is for the same small-rejection cases only.
