# Greatest common divisor (Euclid)

Write `gcd(a, b)` for whole numbers `a, b >= 0`, using Euclid's rule **recursively**:

- `gcd(a, 0) = a`
- `gcd(a, b) = gcd(b, a % b)` when `b > 0`

`gcd(0, 0)` is defined as `0`. `math.gcd` is not allowed: write the recursion.

## Example

```python
>>> gcd(12, 18)
6
>>> gcd(17, 5)
1
>>> gcd(0, 9)
9
```

## Constraints

- `0 <= a, b <= 10**18`

## Think about

Why does the recursion always end? Look at the second argument: what happens to it at every step? (It shrinks quickly: the depth is at most about 90 even for numbers near `10**18`.)
