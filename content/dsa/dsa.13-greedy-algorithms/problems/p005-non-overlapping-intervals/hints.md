## Hint 1

You cannot try every set of removals (there are `2^n`). Turn the question around: removing the **fewest** is keeping the **most**. Which greedy from chapter section 4 keeps the most non-overlapping intervals?

## Hint 2

Run activity selection (sort by end time, keep an interval when `start >= last_end`) and count what you keep. Every interval you did not keep must go. Negative start times can appear, so start `last_end` at `float("-inf")`, not at 0.

## Hint 3

```
kept = 0
last_end = -infinity
for (s, e) in intervals sorted by end:
    if s >= last_end:
        kept += 1
        last_end = e
return len(intervals) - kept
```
