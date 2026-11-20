## Approach

```python
import sys

P = 10**9 + 7
data = sys.stdin.read().split()
q = int(data[0])
ns = data[1::2][:q]
rs = data[2::2][:q]
N = max(map(int, ns))

fact = [1] * (N + 1)
for i in range(1, N + 1):
    fact[i] = fact[i - 1] * i % P
inv_fact = [1] * (N + 1)
inv_fact[N] = pow(fact[N], P - 2, P)
for i in range(N, 0, -1):
    inv_fact[i - 1] = inv_fact[i] * i % P

out = []
for n, r in zip(map(int, ns), map(int, rs)):
    if r > n:
        out.append("0")
    else:
        out.append(str(fact[n] * inv_fact[r] % P * inv_fact[n - r] % P))
print("\n".join(out))
```

Example: `C(5, 2)`: `120 * inv(2) * inv(6)`, and `120 / 12 = 10`. The tables are built once in `O(N)` and every query is `O(1)`.

## Complexity

`O(N + q)` time after one modular exponentiation, `O(N)` memory.

## Another way

Build Pascal's triangle with `C(n, r) = C(n-1, r-1) + C(n-1, r)`: no inverses needed, but `O(N^2)` memory and time, so it only works for `N` up to a few thousand.
