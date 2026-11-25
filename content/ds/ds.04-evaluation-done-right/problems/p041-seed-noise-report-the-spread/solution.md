## Approach

Run, collect, summarise. The spread is the honest error bar for "how good is this pipeline?" when the randomness of the procedure is the main source of variation.

## Code

```python
import numpy as np


def seed_spread(run, seeds):
    scores = [float(run(s)) for s in seeds]
    if len(scores) < 2:
        raise ValueError("need at least two seeds")
    return {"mean": float(np.mean(scores)), "std": float(np.std(scores, ddof=1)),
            "min": float(min(scores)), "max": float(max(scores)), "n": len(scores)}
```

## Complexity

`len(seeds)` runs.

## Another way

Vary the split seed and the model seed separately to see which one causes most of the spread.
