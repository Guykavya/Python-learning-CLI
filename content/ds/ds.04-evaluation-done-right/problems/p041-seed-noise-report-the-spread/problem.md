# Seed noise: report the spread

Chapter section 13. The same pipeline run with a different random seed (for the split, the model, or both) gives a different score. A single number hides that spread; report it.

Write `seed_spread(run, seeds)`. `run` is a function that takes a seed and returns a score. Call it once for every seed and return a dict with:

- `"mean"`, `"std"` (sample standard deviation, `ddof=1`), `"min"`, `"max"` of the scores (floats)
- `"n"`: the number of runs (an int)

At least two seeds are needed (`ValueError` otherwise).

## Example

```text
seed_spread(lambda s: [0.76, 0.78, 0.75, 0.79, 0.77][s], range(5))
-> {"mean": 0.77, "std": 0.0158, "min": 0.75, "max": 0.79, "n": 5}
```
A claimed improvement of 0.01 is inside this spread: it needs more evidence.
