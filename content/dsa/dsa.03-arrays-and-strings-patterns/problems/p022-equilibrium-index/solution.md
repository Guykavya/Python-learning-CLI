## Approach

The left sum at position `i` is a prefix sum, and the right sum is "total minus left minus the element
itself". So one pass with a running `left` answers every position in O(1). Stop at the first match, because
the problem asks for the smallest index.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

total = sum(a)
left = 0
answer = -1
for i in range(n):
    right = total - left - a[i]      # everything after position i
    if left == right:
        answer = i + 1               # 1-based
        break
    left += a[i]

print(answer)
```

For the example the total is 0:

| position | a[i] | left | right | equal? |
|---|---|---|---|---|
| 1 | -7 | 0 | 7 | no |
| 2 | 1 | -7 | 6 | no |
| 3 | 5 | -6 | 1 | no |
| 4 | 2 | -1 | -1 | yes |

## Complexity

O(n) time (one `sum` and one loop), O(1) extra memory besides the input list.

## Another way

Build the full prefix array `P` (`P[0] = 0`, `P[i+1] = P[i] + a[i]`) and test `P[i] == P[n] - P[i+1]`. Same
O(n) time, O(n) memory. A neat check that avoids the subtraction: `2 * left + a[i] == total`.
