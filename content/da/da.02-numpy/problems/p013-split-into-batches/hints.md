## Hint 1

What are the start positions of the batches for `len(x) = 10` and `size = 4`? Which kind of index gives a view: a slice or a list of positions? And what does a slice do when its end is past the end of the array?

## Hint 2

```text
if size <= 0: raise ValueError
starts = 0, size, 2*size, ... while start < len(x)     # range(0, len(x), size)
return [x[start : start + size] for each start]        # slices clip at the end: the last one is shorter
```
