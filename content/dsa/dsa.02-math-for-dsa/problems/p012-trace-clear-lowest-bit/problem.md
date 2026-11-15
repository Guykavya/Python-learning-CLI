# Trace the lowest-bit tricks

Three tricks on the lowest 1-bit of `x` appear all the time:

- `x & (x - 1)` clears the lowest set bit.
- `x & -x` keeps only the lowest set bit.
- `x | (x + 1)` sets the lowest 0-bit.

Predict **exactly** what this program prints. Do not run it. (`bin(n)[2:]` is the binary text of `n`
without the `0b` prefix. `print(..., end=" ")` stays on the same line.)

```python
n = 44
steps = 0
while n:
    print(n, bin(n)[2:], "->", end=" ")
    n = n & (n - 1)
    steps += 1
    print(n)
print("steps", steps)

for x in [12, 40, 7, 8]:
    print(x, bin(x)[2:], "x & -x =", x & -x, " x | (x + 1) =", x | (x + 1), " x ^ (x - 1) =", x ^ (x - 1))
print(5 & 3, 5 | 3, 5 ^ 3)
print(1 << 4, 100 >> 3, 6 & 1, 7 & 1)
```

Write your answer in `answer.txt`, one line per printed line.

## Method

Write each number in binary, line the digits up, and apply the operator column by column.
Subtracting 1 turns the lowest 1 into 0 and every 0 below it into 1. That is why `x & (x - 1)` removes exactly
one bit. In Python, `-x` behaves as if there were infinitely many leading 1-bits (two's complement).

## After you answer

How many iterations did the `while` loop make, and how many 1-bits does 44 have? Why are these two numbers equal?
