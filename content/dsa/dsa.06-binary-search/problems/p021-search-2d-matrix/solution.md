## Approach

Treat the matrix as one sorted array of length `R*C` without building it: translate the virtual index with `// C` and `% C`, and run the closed binary search.

## Code

```python
r, c = map(int, input().split())
m = [[int(x) for x in input().split()] for _ in range(r)]
q = int(input())
queries = [int(x) for x in input().split()]
out = []
for x in queries:
    lo, hi = 0, r * c - 1
    ans = "-1 -1"
    while lo <= hi:
        mid = (lo + hi) // 2
        v = m[mid // c][mid % c]
        if v == x:
            ans = f"{mid // c} {mid % c}"
            break
        elif v < x:
            lo = mid + 1
        else:
            hi = mid - 1
    out.append(ans)
print("\n".join(out))
```

## Complexity

O(q log(R*C)) time, O(1) extra space (the matrix itself is the input).

## Another way

Two searches: first binary search the row (the last row whose first number is `<= x`), then binary search inside that row. Same complexity, two small loops.
