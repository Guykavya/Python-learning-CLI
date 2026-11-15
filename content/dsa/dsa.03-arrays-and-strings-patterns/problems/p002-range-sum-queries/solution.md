## Approach

Pay O(n) once to build the prefix sums. After that every question is a subtraction: the elements before `l` cancel
out of `p[r] - p[l-1]`, leaving exactly positions `l..r`.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

p = [0]
for x in a:
    p.append(p[-1] + x)

q = int(input())
out = []
for _ in range(q):
    l, r = map(int, input().split())
    out.append(p[r] - p[l - 1])

print("\n".join(map(str, out)))
```

## Complexity

O(n + q) time instead of O(n * q). Memory O(n) for `p` (plus the list of answers). Collecting the answers and
printing them once is a little faster than 200000 separate `print` calls, but both are fine here.

## Another way

You could answer with `sum(a[l-1:r])`. It is correct, and for a few questions it is all you need. For 200000
questions over 200000 elements it does up to 4 * 10^10 additions. Prefix sums trade a little memory for that time.
