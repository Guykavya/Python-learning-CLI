# Trace a gcd and lcm table

The program below prints one line per pair: `a b gcd lcm check`. The check column tests the identity
`gcd * lcm == a * b`. Predict **exactly** what it prints. Do not run it.

```python
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def lcm(a, b):
    g = gcd(a, b)
    if g == 0:
        return 0
    return a // g * b


pairs = [(12, 18), (7, 13), (0, 5), (9, 9), (100, 75), (1, 1000), (0, 0), (5, 0), (8, 12)]
for a, b in pairs:
    g = gcd(a, b)
    print(a, b, g, lcm(a, b), g * lcm(a, b) == a * b)
```

Write your answer in `answer.txt`, one line per printed line. Booleans print as `True` and `False`.

## How to work

For every pair, run the Euclid loop by hand: `(a, b) -> (b, a % b)` until `b` is 0. Write the pairs you go through.
Zero is the interesting case: what does the loop do when the very first `b` is 0? What when `a` is 0?

## After you answer

1. Does any row print `False` in the last column? Does the identity still hold when a number is 0?
2. What is `gcd(0, 5)`? What is `gcd(0, 0)`? Why does the code need `if g == 0` in `lcm`?
3. Why is `a // g * b` used instead of `a * b // g`? (Think about numbers near 10^18 in C++.)
