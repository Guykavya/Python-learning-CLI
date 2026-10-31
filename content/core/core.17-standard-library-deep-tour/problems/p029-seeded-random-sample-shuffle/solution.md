## Approach

A `random.Random(seed)` object is a generator with its own state. Creating it inside each
function makes every call independent and repeatable: the same seed always starts the same
sequence. Using the module functions after `random.seed(seed)` would also repeat, but it resets
the **shared** generator that every other module uses, which silently changes their "random"
behaviour: a nasty action at a distance. A test checks for exactly that.

`shuffle` works in place, so shuffle a copy. `sample` picks without replacement (no repeats).
`randint(1, 6)` includes both ends.

## Code

```python
import random
from typing import TypeVar

T = TypeVar("T")


def shuffled(items: list[T], seed: int) -> list[T]:
    result = list(items)
    random.Random(seed).shuffle(result)
    return result


def pick_winners(names: list[str], k: int, seed: int) -> list[str]:
    return random.Random(seed).sample(names, k)


def roll_dice(n: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    return [rng.randint(1, 6) for _ in range(n)]


def split_data(items: list[T], test_percent: int, seed: int) -> tuple[list[T], list[T]]:
    if not 0 <= test_percent <= 100:
        raise ValueError("test_percent must be between 0 and 100")
    mixed = shuffled(items, seed)
    n_test = len(mixed) * test_percent // 100
    return mixed[n_test:], mixed[:n_test]
```

## Complexity

`shuffle` and `sample` are O(n) and O(k); the dice are O(n). Memory O(n) for the copies.

## Another way

`rng.sample(items, len(items))` also returns a shuffled new list without touching the input.
For many dice at once, `rng.choices(range(1, 7), k=n)` is shorter, but it uses a different method
internally, so its numbers differ from `randint` for the same seed (still repeatable). Never use
any of these for passwords or tokens: they are predictable by design. That is what `secrets` is
for (next problem).
