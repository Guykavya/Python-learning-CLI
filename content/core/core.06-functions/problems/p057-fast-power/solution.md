## Approach

Halving the exponent at each level means about log₂(exp) levels: 17 for 100,000, far below the
recursion limit. The base case is `exp == 0`. Computing `half` once is essential: two separate
recursive calls per level would double the calls at every level, undoing the gain.

## Code

```python
def power(base, exp):
    """Return base ** exp for integer exp >= 0, recursively, in O(log exp) calls."""
    if exp == 0:
        return 1
    half = power(base, exp // 2)
    if exp % 2 == 0:
        return half * half
    return half * half * base
```

## Complexity

O(log exp) multiplications and recursion depth (each multiplication of big ints costs more as numbers grow).

## Another way

The same idea as a loop, reading the bits of the exponent ("exponentiation by squaring"):
```python
result = 1
while exp > 0:
    if exp % 2 == 1:
        result *= base
    base *= base
    exp //= 2
return result
```
