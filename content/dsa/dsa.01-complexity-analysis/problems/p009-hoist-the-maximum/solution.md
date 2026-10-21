## Approach

`max(a)` walks through the whole list, so it is an O(n) operation, even though it looks like a single word.
The starter calls it twice per pass, `2n` times in all: O(n^2). The highest score never changes, so compute it
once and store it.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

best = max(a)
top = 0
half = 0
for x in a:
    if x == best:
        top += 1
    if 2 * x >= best:
        half += 1
print(top)
print(half)
```

## Complexity

O(n) time: one pass for `max`, one pass for the loop. O(1) extra space. The starter is O(n^2).

## Another way

`top = a.count(best)` and `half = sum(1 for x in a if 2 * x >= best)`. Each is one O(n) pass, so the total is
still O(n), with built-in loops that run faster than a Python `for`.

Other built-ins that hide an O(n) loop: `min`, `sum`,
`list.count`, `list.index`, `x in list`, `sorted` (O(n log n)), slicing `a[i:j]` (copies). Before you put one
of them inside a loop, ask whether its answer changes on each pass.
