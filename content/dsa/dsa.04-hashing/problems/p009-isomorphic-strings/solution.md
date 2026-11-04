## Approach

Check the mapping in both directions. `forward[a] = b` remembers where `a` goes. `backward[b] = a` remembers where `b`
came from. When a pair `(a, b)` arrives, both memories must agree with it (or have no entry yet).

## Code

```python
s = input().strip()
t = input().strip()

forward = {}
backward = {}
answer = "YES"
for a, b in zip(s, t):
    if forward.get(a, b) != b or backward.get(b, a) != a:
        answer = "NO"
        break
    forward[a] = b
    backward[b] = a
print(answer)
```

`forward.get(a, b)` returns the stored target, or `b` itself when `a` is new, so "new" passes the check.

## Complexity

O(n) time, O(k) memory for `k` distinct characters.

## Another way

Convert each string to a **pattern of first appearances** (`egg` becomes `0 1 1`, `add` becomes `0 1 1`) and compare
the patterns. This is the same idea as a canonical key for grouping.
