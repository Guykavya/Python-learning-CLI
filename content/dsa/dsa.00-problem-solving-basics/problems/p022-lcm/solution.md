## Approach

Every common factor of `a` and `b` is also a factor of `a % b`, and the other way round. So
`gcd(a, b) == gcd(b, a % b)`. Repeating this shrinks the numbers very fast, and when the second number
becomes 0 the first one is the GCD (because `gcd(x, 0) == x`). This is Euclid's algorithm.

Then `lcm = a // g * b`. Dividing first keeps the middle value small, and `//` keeps everything an exact
integer. With `/` Python would make a float, which only holds about 16 significant digits, so a 30-digit
answer would come out wrong (and with `.0` or `e+` notation).

## Trace

Input `21` then `6`:

| round | x | y | x % y |
|---|---|---|---|
| start | 21 | 6 | 3 |
| 1 | 6 | 3 | 0 |
| 2 | 3 | 0 | (loop ends) |

`g = 3`, and `21 // 3 * 6 = 7 * 6 = 42`. Printed: `42`.

## Code

```python
a = int(input())
b = int(input())

x = a
y = b
while y != 0:
    x, y = y, x % y
g = x

print(a // g * b)
```

## Complexity

Euclid's algorithm needs about O(log(min(a, b))) rounds: for numbers near 10 to the power 18 that is under
a hundred rounds. Space is O(1). The obvious method, counting `a, 2a, 3a, ...` until one is divisible by `b`,
can need `b` rounds, which for coprime numbers near 10 to the power 18 would never finish.

## Another way

**Subtraction form of Euclid.** Instead of `%`, repeatedly subtract the smaller number from the larger
until they are equal; that common value is the GCD. It is the same idea and easier to see by hand, but
for a pair like `(10**18, 1)` it would subtract a quintillion times. `%` does many subtractions in one step,
so always prefer it in code. The counting-multiples method is fine only when the numbers are tiny,
for example as a quick check of your answer.

## Edge cases

- `a == b`: the GCD is `a`, so the LCM is `a`.
- One divides the other: the LCM is the larger one.
- Coprime numbers (GCD 1): the LCM is the product `a * b`.
