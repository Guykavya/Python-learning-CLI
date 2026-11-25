## Approach

The model answer is in `answer.md`. Three ideas carry it: an integer seed fully decides a stream (so seed arithmetic makes runs share streams), a generator is state (so copies repeat each other), and `spawn` is the tool built to derive many independent, reproducible children from one seed.

## Code

```python
import numpy as np

def make_worker_rngs(seed, n_workers):
    children = np.random.SeedSequence(seed).spawn(n_workers)
    return [np.random.default_rng(child) for child in children]

rngs = make_worker_rngs(100, 8)
```

Calling `make_worker_rngs(100, 8)` twice gives generators that produce the same numbers, worker by worker; no two workers' streams are the same.

## Complexity

Spawning costs almost nothing (a few hashes per child), so there is no reason to avoid it.

## Another way

`np.random.default_rng(seed).spawn(n)` (Ch. 13.5) spawns child generators directly from a parent generator. For a fixed-size job you can also give every worker the same seed with a different, documented `SeedSequence(seed, spawn_key=(i,))`, which is what `spawn` does for you.
