## Approach

Euclid: `gcd(a, b) = gcd(b, a % b)`. Go down until `b = 0`, where `gcd = a` with `x = 1, y = 0`. On the way back up, if the
inner call gives `b*x1 + (a % b)*y1 = g`, then, since `a % b = a - (a // b)*b`,

`a*y1 + b*(x1 - (a // b)*y1) = g`,

so the outer call returns `(g, y1, x1 - (a // b)*y1)`.

Worked example `ext(17, 5)`: `ext(5, 2)` -> `ext(2, 1)` -> `ext(1, 0) = (1, 1, 0)`.
`ext(2, 1)`: `q = 2`, returns `(1, 0, 1 - 2*0) = (1, 0, 1)`: check `2*0 + 1*1 = 1`.
`ext(5, 2)`: `q = 2`, returns `(1, 1, 0 - 2*1) = (1, 1, -2)`: check `5 - 4 = 1`.
`ext(17, 5)`: `q = 3`, `x1 = 1`, `y1 = -2`, so it returns `(1, -2, 1 - 3*(-2)) = (1, -2, 7)`:
`17*(-2) + 5*7 = -34 + 35 = 1`. The program prints `1 -2 7`.

## Code

```python
def ext(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext(b, a % b)
    return g, y1, x1 - (a // b) * y1


q = int(input())
for _ in range(q):
    a, b = [int(x) for x in input().split()]
    g, x, y = ext(a, b)
    print(g, x, y)
```

## Complexity

O(log min(a, b)) steps per query: at most about 90 for numbers up to 10^18, since the remainder at least halves every
two steps. The numbers `x`, `y` stay at most about `b/g` and `a/g` in size.

## Another way

The loop version keeps the pairs `(old_r, r)`, `(old_s, s)`, `(old_t, t)`:

```python
old_r, r = a, b
old_s, s = 1, 0
old_t, t = 0, 1
while r != 0:
    q = old_r // r
    old_r, r = r, old_r - q * r
    old_s, s = s, old_s - q * s
    old_t, t = t, old_t - q * t
print(old_r, old_s, old_t)
```

It gives the same output as the recursive algorithm and avoids recursion limits in other languages.
