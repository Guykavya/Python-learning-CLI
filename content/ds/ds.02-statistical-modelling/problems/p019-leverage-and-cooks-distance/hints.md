## Hint 1

Where does statsmodels keep Cook's distances? Look at `result.get_influence()`.

## Hint 2

```text
cooks = result.get_influence().cooks_distance[0]     # [0] is the distances, [1] their p-values
thr = 4 / n if threshold is None else threshold
positions = [i for i in argsort(-cooks) if cooks[i] > thr]
```
