## Approach

Choose `n` distinct row **positions** at random and take those rows. Sorting is not needed, and the repeated row disappears because no position is chosen twice.

## Code

```python
def draw(pop, n, rng):
    idx = rng.choice(len(pop), n, replace=False)
    return pop.iloc[idx]
```

## Complexity

O(n) for the draw (plus copying n rows).

## Another way

`pop.sample(n, random_state=rng)` also works with a `Generator` in recent pandas. A random sample is unbiased on average, not in each draw: any single sample still has sampling error.
