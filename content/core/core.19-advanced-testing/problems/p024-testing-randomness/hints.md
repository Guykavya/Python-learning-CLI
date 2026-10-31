## Hint 1

Where do the random numbers come from when `rng` is given? When it is `None`? What object has the methods
`sample` and `randint`? (Not the module-level functions: look at `random.Random`.)

## Hint 2

Start each function with `if rng is None: rng = random.Random()`. Validate first, then draw.
`rng.sample` already returns a new list and leaves its input alone; keep it that way.

## Hint 3

```
import random
draw_winners: validate 0 <= k <= len(entries); return rng.sample(entries, k)
roll_dice:    validate count >= 0;             return [rng.randint(1, 6) for _ in range(count)]
default rng:  random.Random()   # own generator, global state untouched
```
