## Approach

A `random.Random(seed)` object is a generator with its own private state. Passing it in gives the
test full control: the same seed gives the same numbers, so the expected value can be computed with
another `Random(seed)`. Creating `random.Random()` as the default keeps production code random without
touching the shared global generator.

## Code

```python
import random


def draw_winners(entries, k, rng=None):
    if rng is None:
        rng = random.Random()
    if k < 0 or k > len(entries):
        raise ValueError("k must be between 0 and len(entries)")
    return rng.sample(entries, k)


def roll_dice(count, rng=None):
    if rng is None:
        rng = random.Random()
    if count < 0:
        raise ValueError("count must not be negative")
    return [rng.randint(1, 6) for _ in range(count)]
```

## Complexity

`draw_winners` is O(k) after validation; `roll_dice` is O(count).

## Another way

Accept a **function** (`randint`) instead of a whole generator, or let tests pass a tiny stub with a
fixed `randint`. A stub makes the test independent of the exact algorithm of `random`.
