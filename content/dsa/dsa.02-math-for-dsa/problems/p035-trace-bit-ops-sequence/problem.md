# Trace a bit operations sequence

Predict **exactly** what this program prints. Do not run it. Python integers are arbitrary-length two's complement
numbers: a negative number behaves as if it had infinitely many leading 1 bits, and `~x` is `-x - 1`.

```python
x = 45                       # binary 101101
print(x >> 2, x << 3, x & 15, x | 2, x ^ 63)

a = 12
b = 10
a = a ^ b
b = a ^ b
a = a ^ b
print(a, b)

print(~5, ~0, ~-1)
print(-1 >> 1, -8 >> 1, -7 >> 1, 7 >> 1)
print(-5 & 3, -5 | 3, -5 ^ 3)
print(-5 & 255, bin(5), bin(-5))
print(7 & -7, 12 & -12, 40 & -40)
print(1 << 10, (1 << 10) - 1, 5 & 5 - 1)
```

Write your answer in `answer.txt`, one line per printed line, with values separated by single spaces, for example
`1 2 3 4 5` (not the real answer).

## How to work

- Write each number in binary below the other, aligned on the right. Do the operation bit by bit.
- For negative numbers use `-x = ~x + 1`, so `-5` is `...11111011` (infinitely many 1s on the left).
- `a >> k` is floor division by `2^k`, so it rounds toward minus infinity: `-7 >> 1` is `-4`, not `-3`.
- The last two lines contain a priority trap: in `5 & 5 - 1`, which operator binds tighter, `&` or `-`?

## After you answer

1. After the XOR swap, what are `a` and `b`? Why does it work, and why would it break with `a ^= a`?
2. `x & -x` isolates the lowest set bit. Check it against the three values on the line `7 & -7 ...`.
3. Why is `bin(-5)` not a string of 0s and 1s with a sign convention like `0b...11111011`?
