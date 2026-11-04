## Approach

Precompute the prefix hashes `P` and the powers of `B`. A query is one subtraction and one multiplication, all modulo `M`.
Python's `%` returns a non-negative result for a positive modulus, so a negative difference is fixed automatically.

## Code

```python
B = 131
M = 1_000_000_007

s = input().strip()
q = int(input())

P = [0]
pw = [1]
for ch in s:
    P.append((P[-1] * B + (ord(ch) - 96)) % M)
    pw.append(pw[-1] * B % M)

out = []
for _ in range(q):
    l, r = map(int, input().split())
    out.append((P[r] - P[l - 1] * pw[r - l + 1]) % M)
print("\n".join(map(str, out)))
```

## Complexity

O(n + q) time and O(n) memory.

## Another way

A single hash with `M = 10^9 + 7` is fine for 2 * 10^5 queries here because each value is **printed**, not compared. When hashes are used to test
equality, collisions matter: use a larger modulus (2^61 - 1) or two moduli (double hashing, section 8 of the chapter).
