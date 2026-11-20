## Approach

```python
import copy
import random


def _call(f, case):
    try:
        return f(*copy.deepcopy(case))
    except Exception as e:
        return e


def _same(a, b):
    if isinstance(a, Exception) or isinstance(b, Exception):
        return isinstance(a, Exception) and isinstance(b, Exception) and type(a) is type(b)
    return a == b


def stress(fast, brute, gen, trials=1000, seed=1):
    rng = random.Random(seed)
    for _ in range(trials):
        case = gen(rng)
        a = _call(fast, case)
        b = _call(brute, case)
        if not _same(a, b):
            return case, a, b
    return None
```

Each function gets `copy.deepcopy(case)`, so an in-place sort inside `fast` cannot change what `brute` or the caller sees. `random.Random(seed)` is made once outside the loop, so every run with the same seed visits the same cases, and a failure can be reproduced by anyone.

Example: with the buggy Kadane of the statement and seed 1, the first failing case is a short list of negative numbers; `fast` returns 0 (the empty sum) and `brute` returns the best negative number.

## Complexity

`O(trials * (cost of fast + cost of brute))`.

## Another way

A `for trial in range(trials)` loop that creates `random.Random(seed + trial)` for every trial: each failing trial can then be replayed alone from its own seed (`seed + trial`). The cost is a new generator object per trial.
