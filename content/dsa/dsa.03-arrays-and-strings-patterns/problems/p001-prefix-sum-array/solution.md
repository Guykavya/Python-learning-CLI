## Approach

Keep a running total. The list starts with `0` and every element adds one new cell: the last cell plus that element.
No element is ever added twice.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

p = [0]
for x in a:
    p.append(p[-1] + x)

print(*p)
```

## Complexity

O(n) time: one addition per element. O(n) extra memory for the `n + 1` cells.

## Another way

`itertools.accumulate(a, initial=0)` yields exactly `0, a[0], a[0]+a[1], ...`, so `print(*accumulate(a, initial=0))`
is the one-line version. The slow way is `sum(a[:i])` for every `i`: it adds the same elements again and again,
which is about `n * n / 2` additions (2 * 10^10 for `n = 200000`).
