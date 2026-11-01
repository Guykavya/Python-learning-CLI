# Comprehension or loop?

A comprehension says "build a collection from another one" in one line. A generator
expression does the same **lazily**, one item at a time. But not every loop should become
a comprehension. Use these rules:

| Situation | Tool |
|---|---|
| build a list / dict / set from items, maybe filtering | comprehension |
| count, sum, test "any" / "all" | `sum(...)`, `any(...)`, `all(...)` with a **generator expression** (round brackets, no list in between) |
| each step has a **side effect** (log, print, write) | loop |
| you must **stop early** (`return` at the first hit) | loop (or `any`, `next`) |
| three or more nested `for` clauses | loop or helper function: unreadable |

`starter.py` has eight functions. Some are already the right shape. Copy it to `solution.py`,
fix the ones that are not, and leave the others alone. Keep names and parameters.

Checks beyond behaviour:

- `squares_of_evens` uses a list comprehension, `word_lengths` a dict comprehension. None of the
  first five functions may contain a `for`/`while` **statement**.
- `count_long` and `any_big` must not build a list inside square brackets. `any_big` is also
  tested on a stream of a million numbers: it must read only until the first match.
- `log_and_double` and `first_duplicate` must keep a `for` loop. `first_duplicate` is tested to
  stop reading right after the repeat. `log` must not be called inside a comprehension.
- No comprehension in the file may have more than two `for` clauses. `pythagorean_triples`
  currently uses three nested loops; make it faster **and** readable (hint: given `a` and `b`,
  `c` is not a free choice).

**Example**

```python
squares_of_evens([1, 2, 3, 4])      # [4, 16]
word_lengths("the quick fox")       # {'the': 3, 'quick': 5, 'fox': 3}
any_big(range(10**9), 4)            # True, instantly
first_duplicate([1, 2, 3, 2, 9])    # 2
```
