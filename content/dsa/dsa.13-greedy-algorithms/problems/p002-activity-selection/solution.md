## Approach

Earliest finish first (chapter section 4). Sort the events by end time. Walk through them, keeping the end of the last event taken. An event that starts at or after that end fits, so take it and move `last_end` forward; any other event overlaps the last one taken and is skipped for ever.

```python
def max_activities(intervals):
    count = 0
    last_end = float("-inf")
    for s, e in sorted(intervals, key=lambda iv: (iv[1], iv[0])):
        if s >= last_end:              # fits after the last chosen event (touching is fine)
            count += 1
            last_end = e
    return count
```

Why it is safe: the event `g` that ends first can replace the first event of any optimal schedule without causing an overlap (exchange argument, problem p001), and what is left is the same problem on the events that start at or after `end(g)`.

## Complexity

`O(n log n)` for the sort, `O(n)` for the sweep, `O(n)` extra space for the sorted copy.

## Another way

Sort by **start**, but walk from the **end** backwards and take the event that **starts latest**: the mirror image of earliest finish. Or keep the earliest-finish sweep but write it as "when two events overlap, drop the one that ends later" (chapter section 5); it is the same algorithm.
