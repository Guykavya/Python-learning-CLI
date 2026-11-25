## Hint 1

`np.argpartition(x, -k)` returns positions arranged so that the last `k` of them point at the `k` largest values, in no particular order (Ch. 15.3). How many values do you still need to sort after that?

## Hint 2

Sort only the winners: `x[idx]` has `k` values; `np.argsort` of those gives their ascending order; reverse it for best first, and use it to reorder `idx` (not `x`). Then think about `k = 0`: what is `-0`, and what does `[-0:]` select?

## Hint 3

```text
if k < 0: raise ValueError
k = min(k, len(x));  if k == 0: return empty integer array
idx = argpartition(x, -k)[-k:]
return idx[argsort(x[idx])[::-1]]
```
