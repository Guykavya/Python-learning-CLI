# Fast power that halves the problem

Write `power(base, exp)` for an integer `exp >= 0`, **recursively**, without `**` and without
`pow`.

The obvious recursion `base * power(base, exp - 1)` needs `exp` levels and hits the recursion
limit at about 1000. Yours must handle `exp = 100_000`. Use the halving idea:

- `x**0 = 1`
- if `n` is even, `x**n = (x**(n/2))²`
- if `n` is odd, `x**n = (x**(n//2))² × x`

Compute the half power **once** and reuse it.

**Examples**

```python
power(2, 10)        # 1024
power(3, 5)         # 243
power(7, 0)         # 1
power(-2, 3)        # -8
power(1.5, 2)       # 2.25
len(str(power(2, 100_000)))   # 30103 digits
```
