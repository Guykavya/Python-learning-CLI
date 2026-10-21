## Approach

Strip the sign with `abs()`, then pick out each place value with `//` (shift right) and `% 10` (take the last digit).

## Code

```python
n = abs(int(input()))
total = n % 10 + n // 10 % 10 + n // 100 % 10 + n // 1000 % 10
print(total)
print(total % 3 == 0)
```

## Why abs() is needed

For negative numbers `%` returns a non-negative remainder when the divisor is positive:
`-4071 % 10` is `9`, because `-4071 = -408 * 10 + 9`. The digits come out wrong.

## Another way

`divmod` gives quotient and remainder together: `n, d1 = divmod(n, 10)` repeated four times.
Once you learn loops (core.04), a `while n > 0` loop handles any number of digits.
