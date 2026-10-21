## Approach

Rotating right by `k` moves the last `k` items to the front. Two slices do it. Reduce `k`
with `%` so that big and negative values become a shift between 0 and n - 1.

## Code

```python
items = input().split()
k = int(input())
n = len(items)
if n == 0:
    print("(empty)")
else:
    k %= n
    print(" ".join(items[n - k:] + items[:n - k]))
```

## Complexity

O(n): the slices copy every item once.

## The k = 0 trap

With `k = 0`, `items[-0:]` is `items[0:]`, the **whole** list, and `items[:-0]` is `items[:0]`,
empty. The result happens to be right, but by luck. Writing `items[n - k:] + items[:n - k]`
after `k %= n` avoids relying on `-0`.
