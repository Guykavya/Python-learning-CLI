## Hint 1

`np.argsort(x)` answers "which position holds the smallest, the second smallest, ...?". Ranks answer the opposite question: "where in the sorted order does position `i` end up?". How do you invert that mapping? And how do you sort descending **without** reversing the order of tied values?

## Hint 2

```text
key = -x if descending else x               # negate instead of reversing: ties keep their order
order = np.argsort(key, kind="stable")      # stable: equal keys stay in position order
result = empty integer array of length n
result[order] = np.arange(n)                # position order[r] gets rank r
```
