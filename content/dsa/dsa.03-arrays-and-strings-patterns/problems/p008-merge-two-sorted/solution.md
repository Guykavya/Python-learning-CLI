## Approach

Both fronts are the smallest remaining values of their arrays, so the smaller front is the smallest of all that is
left. Take it and repeat. When one array is used up, the other one's leftover tail is already sorted.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
m = int(input())
b = [int(x) for x in input().split()]

i = j = 0
out = []
while i < n and j < m:
    if a[i] <= b[j]:
        out.append(a[i])
        i += 1
    else:
        out.append(b[j])
        j += 1
out.extend(a[i:])
out.extend(b[j:])

print(*out)
```

## Complexity

O(n + m) time: each element is appended once. O(n + m) memory for the result.

## Another way

`sorted(a + b)` is O((n + m) log(n + m)) and ignores the fact that both halves are already sorted.
`heapq.merge(a, b)` does the same two-pointer merge for you. Using `<=` (take from `a` on ties) keeps equal elements
in their original order, which makes merge sort *stable*.
