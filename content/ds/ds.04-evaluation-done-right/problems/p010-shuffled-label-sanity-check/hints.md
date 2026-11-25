## Hint 1

Why does the function take a whole *procedure* (a function) and not a model? Which part of a leaky procedure would a model never see?

## Hint 2

```text
rng = default_rng(seed)
scores = [evaluate(rng.permutation(y)) for _ in range(repeats)]
return mean(scores), std(scores)
```
