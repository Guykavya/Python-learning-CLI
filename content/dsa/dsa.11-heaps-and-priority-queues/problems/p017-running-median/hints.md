## Hint 1

Write the numbers `1 2 3 5 8 9` on paper and draw a line through the middle. The left part is the "lower half", the right part the "upper half". Which number of the lower half do you need to find the median: its smallest or its largest? Which number of the upper half? Which kind of heap gives you the **largest** item at the top, if `heapq` only has a min-heap?

## Hint 2

Keep two rules true after every `add`: (1) every number of the lower half is `<=` every number of the upper half; (2) the lower half has the same size as the upper half, or exactly one more. A short way to keep both rules after a new number `x`:

1. push `x` into the lower half;
2. move the largest item of the lower half to the upper half (this fixes rule 1);
3. if the upper half is now bigger, move its smallest item back to the lower half (this fixes rule 2).

## Hint 3

```
low  = []        # max-heap: store -x
high = []        # min-heap

add(x):
    push(low, -x)
    push(high, -pop(low))
    if len(high) > len(low):
        push(low, -pop(high))

median():
    if no numbers: raise ValueError
    if len(low) > len(high): return -low[0]
    return (-low[0] + high[0]) / 2
```
