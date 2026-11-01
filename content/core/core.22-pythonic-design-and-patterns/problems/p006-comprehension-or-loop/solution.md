## Approach

Sort the eight tasks:

| Function | Kind | Result |
|---|---|---|
| `squares_of_evens` | build a list | list comprehension |
| `word_lengths` | build a dict | dict comprehension |
| `count_long` | count | `sum` of a generator expression |
| `any_big` | ask yes/no, may stop | `any` of a generator expression (lazy) |
| `flatten` | build a list from nested | comprehension with 2 `for` clauses |
| `pythagorean_triples` | build, but 3 loops | 2 loops + compute `c` |
| `log_and_double` | side effect | stay a loop |
| `first_duplicate` | early exit | stay a loop |

A list comprehension inside `len(...)` or `sum(...)` builds all items, then throws them away.
A generator expression passes them one at a time and `any` stops at the first `True`.

## Code

```python
from math import isqrt


def squares_of_evens(nums):
    return [n * n for n in nums if n % 2 == 0]


def word_lengths(text):
    return {w: len(w) for w in text.split()}


def count_long(words, n):
    return sum(1 for w in words if len(w) > n)


def any_big(items, limit):
    return any(x > limit for x in items)


def flatten(matrix):
    return [x for row in matrix for x in row]


def pythagorean_triples(n):
    return [
        (a, b, isqrt(a * a + b * b))
        for a in range(1, n + 1)
        for b in range(a + 1, n + 1)
        if isqrt(a * a + b * b) <= n and isqrt(a * a + b * b) ** 2 == a * a + b * b
    ]


def log_and_double(items, log):
    result = []
    for item in items:
        log(item)
        result.append(item * 2)
    return result


def first_duplicate(items):
    seen = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None
```

## Complexity

`pythagorean_triples` drops from O(n^3) to O(n^2): `c` is computed, not searched. The rest are O(n);
`any_big` is O(k) where k is the position of the first match, with O(1) memory.

## Another way

`pythagorean_triples` can stay as two loops with `c = isqrt(...)` and an `if`; the test only
asks for correct output and no 3-clause comprehension. `first_duplicate` could use
`itertools` tricks, but a plain loop with a `set` says it best. `flatten` also works as
`list(itertools.chain.from_iterable(matrix))`.
