## Hint 1

If every 0 counts as -1 and every 1 counts as +1, what does a balanced block add up to?

## Hint 2

Keep a running total `s`. Store the **first** index where each total appeared (the empty prefix has total 0 at index -1). When `s` appears again at index `i`, the block `first+1..i` is balanced.

## Hint 3

```
first = {0: -1}; s = 0; best = 0
for i, x in enumerate(a):
    s += 1 if x == 1 else -1
    if s in first: best = max(best, i - first[s])
    else: first[s] = i
```
