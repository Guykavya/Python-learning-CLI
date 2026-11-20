## Hint 1

A rule loses when its **first** choice is bad. For earliest start: what kind of event starts first but is a terrible choice? For shortest first: where could a short event sit so that taking it blocks **two** good events?

## Hint 2

For `a`: one event that starts at 0 and ends very late, plus three or four short events inside it that do not overlap each other. Earliest start takes the long one and then nothing (or almost nothing) fits.

For `b`: two longer events that touch or nearly touch, like `(0, 6)` and `(7, 13)`, and a short event across the gap, like `(5, 8)`. Shortest first takes `(5, 8)`, which overlaps both. Repeat the pattern twice so the loss is clearer, or keep it once with your own numbers.

## Hint 3

Check each list by hand before you submit:

```
sort a by start -> take/skip with s >= last_end -> count
best for a: the short events only -> count
sort b by length -> take/skip -> count
best for b: the long events only -> count
the greedy count must be smaller (for a, by 2 or more)
```
