# Construct, do not filter

There are two ways to get valid test data:

- **Filter**: generate anything, throw away what is invalid (`.filter(...)` or `assume(...)`). Simple, but when most examples are
  thrown away, hypothesis wastes its time or even gives up with a *health check* error ("filter_too_much").
- **Construct**: generate the data so that it is valid by construction (`.map(...)`, bounds, `unique=True`). Every example counts.

The starter in `solution.py` has five strategies that filter. They give the right data, slowly (or not at all). Rewrite each one
to **construct**:

| Name | Must generate | Hint |
|---|---|---|
| `even_numbers` | even whole numbers from -1000 to 1000 | double a smaller integer |
| `sorted_lists` | lists of at most 10 whole numbers from -50 to 50, ascending (equal neighbours allowed) | sort a generated list |
| `ordered_pairs` | tuples `(a, b)` with `a` from -100 to 100 and `b - a` from 1 to 50 | generate `a` and the gap, build `b` |
| `multiples_of_1000` | multiples of 1000 from -1,000,000 to 1,000,000 | a small integer times 1000 |
| `distinct_lists` | lists of 2 to 8 **different** whole numbers from -20 to 20 | `st.lists` has an argument for this |

Rules:

- Do **not** use `.filter(...)`, `assume(...)` or `.example()` anywhere in `solution.py` (the checker reads your code).
- The values must still cover the whole allowed range, with variety: the checker draws 100 examples and looks at them.

**How this is checked.** For each name the checker draws 100 examples (`@settings(derandomize=True, database=None, max_examples=100)`),
checks that all follow the rule, and looks for variety. If hypothesis has to throw away too much, its health check fails and you get a message about it.

**Example**

```python
# filtered:      st.integers(0, 100).filter(lambda n: n % 5 == 0)     (80% thrown away)
# constructed:   st.integers(0, 20).map(lambda n: n * 5)               (nothing thrown away)
```
