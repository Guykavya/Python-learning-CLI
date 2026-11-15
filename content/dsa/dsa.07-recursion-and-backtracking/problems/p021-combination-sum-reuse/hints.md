## Hint 1

Generate each combination in non-decreasing order of positions: once you have moved past candidate `i`, never go back to it. Then every multiset is built exactly once.

## Hint 2

After choosing `candidates[i]` the next call starts at `i` (the same number may be chosen again), not `i + 1`. The answer is complete when the remaining target is 0.

## Hint 3

```
sort candidates
def go(start, remaining):
    if remaining == 0: record a copy; return
    for i in range(start, len(candidates)):
        if candidates[i] > remaining: break
        path.append(candidates[i]); go(i, remaining - candidates[i]); path.pop()
```
