## Approach

Hash the pattern and the first window with Horner's rule. For each window compare the two integers; on equality verify with a
real string comparison (protects against collisions). Then update the window hash in `O(1)`: subtract the leaving letter's
share `v * B^(m-1)`, multiply by `B`, add the entering letter.

## Code

```python
B = 131
M = 1_000_000_007

t = input().strip()
p = input().strip()
n, m = len(t), len(p)

hp = 0
h = 0
for i in range(m):
    hp = (hp * B + ord(p[i]) - 96) % M
    h = (h * B + ord(t[i]) - 96) % M
top = pow(B, m - 1, M)

found = []
for i in range(n - m + 1):
    if h == hp and t[i:i + m] == p:
        found.append(i)
    if i + m < n:
        h = ((h - (ord(t[i]) - 96) * top) * B + ord(t[i + m]) - 96) % M

print(len(found))
print(*found)
```

## Complexity

O(n + m) expected: `O(1)` per window plus a verification only on a hash match. The worst case (many false matches or a pattern that
really occurs everywhere) can cost O(n * m) for verification; with a good modulus false matches are very rare.

## Another way

Python's `str.find` in a loop (`t.find(p, i + 1)`) is a strong built-in. KMP and the Z-function (a later module) find all occurrences
in O(n + m) with **no** hashing and no collision risk.
