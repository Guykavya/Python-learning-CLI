## Approach

Any number that divides both `a` and `b` also divides `a % b` (because `a % b` is `a` minus a multiple of `b`),
and the other way round. So the pair `(b, a % b)` has exactly the same common divisors as `(a, b)`, and the same GCD.
The second number shrinks every step, so it eventually reaches 0. The GCD of `(g, 0)` is `g`, because every number divides 0.

Take `abs()` of both numbers first. That makes the answer non-negative and keeps `%` simple.

Why not subtract? The older form of Euclid's idea subtracts the smaller number from the larger again and again.
For `(10^18, 1)` that is 10^18 subtractions, which would take thousands of years. One `%` does all those
subtractions in a single step. Trying every divisor from `min(a, b)` downward is just as hopeless.

## Trace

Input `48` then `18`.

| Iteration | `a` | `b` | `a % b` | new `a` | new `b` |
|---|---|---|---|---|---|
| 1 | 48 | 18 | 12 | 18 | 12 |
| 2 | 18 | 12 | 6 | 12 | 6 |
| 3 | 12 | 6 | 0 | 6 | 0 |

`b` is 0, so the loop stops. Output: `6`.

## Code

```python
a = abs(int(input()))
b = abs(int(input()))
while b != 0:
    a, b = b, a % b
print(a)
```

## Complexity

Every two steps, the larger number at least halves. So the loop runs O(log(min(a, b))) times, about 90 steps at most
for numbers up to 10^18. The worst case is a pair of consecutive Fibonacci numbers, where every quotient is 1.

## Another way

Without tuple assignment, use a temporary variable:

```python
while b != 0:
    r = a % b
    a = b
    b = r
```

Same algorithm, three lines. In real code you would write `math.gcd(a, b)`, which uses the same idea.

A related fact worth remembering: the least common multiple is `abs(a * b) // gcd(a, b)`. Computing it from the GCD
is much faster than searching for it.

## Edge cases

- One number is 0: `gcd(0, 5)` is 5 and `gcd(7, 0)` is 7. The loop handles both: `(0, 5)` becomes `(5, 0)`; `(7, 0)` stops at once.
- Negative inputs: `abs()` first, so `gcd(-12, 18)` is 6 and `gcd(-4, -6)` is 2.
- `a < b`: the first step swaps them automatically, because `a % b` is `a` when `a < b`.
