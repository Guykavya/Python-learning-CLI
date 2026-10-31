# Testing randomness

Random code is testable in two ways: **inject** the random generator, or **seed** it. A test that
depends on the global `random` module is shaky, and code that quietly consumes global random numbers
makes other code unpredictable.

In `solution.py` write two functions. Both take an optional `rng` (a `random.Random` object). When
`rng` is `None` they create their own `random.Random()`. **They must never touch the global
`random` functions** (`random.sample`, `random.randint`, ...).

```python
def draw_winners(entries, k, rng=None): ...   # return rng.sample(entries, k), a new list
def roll_dice(count, rng=None): ...           # return [rng.randint(1, 6) for _ in range(count)]
```

- `draw_winners` raises `ValueError` if `k` is negative or larger than `len(entries)`, and must not change `entries`.
- `roll_dice` raises `ValueError` if `count` is negative.
- Take the numbers from the generator in exactly the order given above, so that the same seed gives the
  same result as a reference computed with the same `Random`.

**Example**

```python
import random
draw_winners(["a", "b", "c", "d"], 2, random.Random(7)) == random.Random(7).sample(["a", "b", "c", "d"], 2)   # True
roll_dice(3, random.Random(1)) == [random.Random(1).randint(1, 6) ...]   # same numbers, same order
```
