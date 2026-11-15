## Hint 1

What is the smallest list that is already sorted? That is your base case. How do you shrink every other list to get there?

## Hint 2

Base case: `len(a) <= 1` returns `a`. Otherwise `mid = len(a) // 2`, `left = sort(a[:mid])`, `right = sort(a[mid:])`, and return `merge(left, right)`.

## Hint 3

```
def merge_sort(a):
    if len(a) <= 1: return a
    mid = len(a) // 2
    left = merge_sort(a[:mid]); right = merge_sort(a[mid:])
    return merge(left, right)   # two pointers, <= on ties, then extend the leftovers
```
