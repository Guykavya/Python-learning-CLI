## Approach

Two pointers walk towards each other from the two ends of the part, swapping as they go. Each swap puts two elements
in their final places, so a part of length `m` needs `m // 2` swaps.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
q = int(input())

for _ in range(q):
    l, r = map(int, input().split())
    i, j = l - 1, r - 1
    while i < j:
        a[i], a[j] = a[j], a[i]
        i += 1
        j -= 1

print(*a)
```

## Complexity

O(r - l) per operation, O(n * q) in the worst case (here at most 20 full reversals). O(1) extra memory: that is
what "in place" means.

## Another way

`a[l-1:r] = a[l-1:r][::-1]` does the same work using a temporary copy of the part. The three-reversal rotation from
the example (reverse all, reverse the first `k`, reverse the rest) rotates right by `k` in place, with O(1) extra
memory.
