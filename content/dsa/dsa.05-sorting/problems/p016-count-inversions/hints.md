## Hint 1

During a merge, left and right halves are sorted. Suppose you take `right[j]` because it is smaller than `left[i]`. What do you know about `left[i+1]`, `left[i+2]`, ...?

## Hint 2

They are all `>= left[i]`, hence all `> right[j]`. So each such step adds `len(left) - i` inversions. When the values are equal the left value goes first (`<=`), and nothing is counted.

## Hint 3

```
def sort_count(a):
    if len(a) <= 1: return a, 0
    left, x = sort_count(a[:mid]); right, y = sort_count(a[mid:])
    merge; on taking right[j]: count += len(left) - i
    return merged, x + y + count
```
