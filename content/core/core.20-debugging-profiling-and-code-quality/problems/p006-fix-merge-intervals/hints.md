## Hint 1

Take the reports one at a time and shrink each to a two-interval input:
`[[1, 3], [3, 5]]`, `[[9, 17], [10, 11]]`, `[[1, 3], [2, 6]]` (then print the caller's list),
`[]`, `[(1, 2), (2, 4)]`. Put `breakpoint()` as the first line of the loop and use
`p start, end, last, merged`. Which comparison or assignment is wrong for each one?

## Hint 2

Two reports are about **aliasing**. `intervals.sort()` changes the caller's list. And
`merged = [intervals[0]]` puts the caller's own pair object into `merged`, so `last[1] = ...`
writes into the caller's data (and fails for tuples). Ask: "which object does this name point
to?" Check with `p last is intervals[0]` at the prompt.

## Hint 3

```
merged = []
for start, end in sorted(intervals):          # new list, caller's order untouched
    if merged and start <= merged[-1][1]:     # touching counts; empty input is fine
        merged[-1][1] = max(merged[-1][1], end)
    else:
        merged.append([start, end])           # a NEW pair
return merged
```
