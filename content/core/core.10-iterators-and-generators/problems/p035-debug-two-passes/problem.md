# Debug: functions that read a generator twice

Ravi wrote two helper functions. His tests use lists, and they pass. In real use the numbers come
from a generator, and the results are wrong or the program crashes. `starter.py` holds his code.

```python
def stats(numbers):
    count = len(list(numbers))
    total = sum(numbers)
    largest = max(numbers) if count else None
    return count, total, largest


def shares(numbers):
    total = sum(numbers)
    return [x / total for x in numbers]
```

Fix both functions in `solution.py` so they work for **any iterable**: a list, a tuple, a
`range`, a generator or a generator expression.

1. `stats(numbers)` returns a tuple `(count, total, largest)`.
   - For no numbers it returns `(0, 0, None)`.
   - It must make **one pass** over the input and must **not** build a list of all the numbers
     (the input may be huge). Use O(1) extra memory.
2. `shares(numbers)` returns a list: each number divided by the total of all numbers.
   - This one truly needs two passes (first the total, then the divisions). Find a correct way.
   - If the total is `0` (this includes an empty input), raise `ValueError` with a clear message.

**Examples**

```python
stats(x for x in [4, 9, 2])        # (3, 15, 9)
stats(iter([]))                    # (0, 0, None)
shares(x for x in [1, 1, 2])       # [0.25, 0.25, 0.5]
shares([5, -5])                    # raises ValueError
```

Before you change anything, run `stats(x for x in [4, 9, 2])` with Ravi's code and explain to
yourself why it fails.
