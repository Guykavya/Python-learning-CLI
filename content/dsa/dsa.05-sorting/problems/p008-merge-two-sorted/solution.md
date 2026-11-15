## Approach

Two indices walk forward. Each round puts the smaller front value into the output. After one list runs out, append the tail of the other.

## Code

```python
n, m = map(int, input().split())
a = [int(x) for x in input().split()]
b = [int(x) for x in input().split()]
out = []
i = j = 0
while i < n and j < m:
    if a[i] <= b[j]:
        out.append(a[i])
        i += 1
    else:
        out.append(b[j])
        j += 1
out.extend(a[i:])
out.extend(b[j:])
print(" ".join(map(str, out)))
```

## Complexity

O(n + m) time, O(n + m) memory for the output.

## Another way

Merge from the back (largest first) into a pre-sized list, as LeetCode 88 does in place. Or `heapq.merge`, which is lazy and handles many lists, but is banned here.
