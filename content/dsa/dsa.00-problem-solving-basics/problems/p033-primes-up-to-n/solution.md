## Approach

Test each `x` from 2 to `n` with **trial division**: try divisors `d` and stop at the first one that divides `x`.

The key fact: if `x = a * b` with `a <= b`, then `a * a <= a * b = x`. So if `x` has any divisor
(other than 1 and itself), it has one with `d * d <= x`. We never need to try past the square root.
For `x = 199999` that is about 447 tries instead of about 200000.

The reference also skips even numbers above 2 (they are divisible by 2) and only tries odd divisors
3, 5, 7, ... This roughly halves the work twice over.

The primes are collected in a text variable `line`, with a space put before every prime except the first,
so there are no extra spaces. If no prime was found, `line` is not printed at all.

## Trace

Checking `x = 25` (odd, so we test odd divisors from 3):

| `d` | `d * d` | `d * d <= 25`? | `25 % d` | action |
|---|---|---|---|---|
| 3 | 9 | yes | 1 | go on, `d` becomes 5 |
| 5 | 25 | yes | 0 | not prime, `break` |

With the wrong condition `d * d < x`, the loop stops before `d = 5` and 25 is reported as prime.
That is why the tests include `n = 25`.

## Code

```python
n = int(input())
count = 0
line = ""
for x in range(2, n + 1):
    if x % 2 == 0 and x != 2:
        continue  # even numbers above 2 are never prime
    is_prime = True
    d = 3
    while d * d <= x:
        if x % d == 0:
            is_prime = False
            break
        d += 2
    if is_prime:
        count += 1
        if line == "":
            line = f"{x}"
        else:
            line = line + " " + f"{x}"
if count > 0:
    print(line)
print(f"count {count}")
```

## Complexity

Each number needs at most about `sqrt(x)` tries, so the total is about `n * sqrt(n)` steps:
O(n * sqrt(n)), roughly 200000 * 447 / 4 = 22 million steps at worst for the reference, and much
less in practice because most numbers have a small divisor. The naive "divide by everything below `x`"
is O(n^2) for the primes, about 2 billion steps here, which takes minutes in Python.

## Another way

The **Sieve of Eratosthenes** crosses out multiples of each prime in a table of `n + 1` true/false
values, and is O(n log log n), much faster for large `n`. It needs a list, which you will learn soon.
Prefer the sieve when you need all primes up to a large `n`; prefer trial division when you test
only a few numbers.

## Edge cases

- `n = 0` or `n = 1`: the loop never runs; only `count 0` is printed.
- `n = 2`: the only prime is 2. The even-number skip must not skip 2 itself.
- Perfect squares of primes (9, 25, 49): caught only if the loop condition is `d * d <= x`.
