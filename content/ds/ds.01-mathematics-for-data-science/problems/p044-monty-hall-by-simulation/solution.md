## Approach

Simulate the rules exactly and count wins; switching wins exactly when the first pick was a goat (2 of 3 times).

## Code

```python
import numpy as np


def monty_hall(switch, trials, seed=0):
    rng = np.random.default_rng(seed)
    wins = 0
    for _ in range(trials):
        car = int(rng.integers(3))
        pick = int(rng.integers(3))
        options = [d for d in range(3) if d != pick and d != car]
        opened = int(options[int(rng.integers(len(options)))])
        if switch:
            pick = next(d for d in range(3) if d != pick and d != opened)
        wins += pick == car
    return wins / trials
```

## Complexity

O(trials).

## Another way

Use 100 doors: the host opens 98 goats and switching wins 99% of the time, which makes the logic obvious.
