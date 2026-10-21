## Approach

Our numbers are written in base 10. Dividing by 10 moves every digit one place to the right.
The remainder is the digit that falls off.

## Code

```python
n = int(input())
print(n % 10)
print(n // 10)
print(n // 10 % 10)
```

## Why it works

`1234 = 123 * 10 + 4`, so `1234 // 10` is `123` and `1234 % 10` is `4`.
This works for any size of integer, because Python ints have arbitrary precision.

## Another way

`divmod(n, 10)` returns both at once: `rest, last = divmod(n, 10)`.
