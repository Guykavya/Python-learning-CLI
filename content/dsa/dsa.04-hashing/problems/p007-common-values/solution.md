## Approach

Turn both lists into sets (this also drops repeats), intersect them, and sort the result for printing.

## Code

```python
n, m = map(int, input().split())
a = [int(x) for x in input().split()]
b = [int(x) for x in input().split()]

common = sorted(set(a) & set(b))
print(len(common))
print(*common)
```

`print(*common)` with an empty list prints an empty line, which is what the problem asks for.

## Complexity

O(n + m) on average to build the sets and intersect (the intersection loops over the smaller set), plus O(c log c)
to sort `c` common values.

## Another way

Sort both lists and walk two pointers (dsa.03): O(n log n + m log m), no hashing. The set solution is shorter and
usually faster.
