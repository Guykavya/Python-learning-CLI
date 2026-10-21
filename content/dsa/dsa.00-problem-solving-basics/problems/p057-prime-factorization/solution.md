## Approach

**Trial division.** Keep `m`, the part of `n` not yet factored. Try divisors `d = 2, 3, 4, ...`. When
`d` divides `m`, divide it out completely, counting how many times (`e`). Because all smaller primes
have already been divided out, any `d` that still divides `m` must be prime: 4 can never divide `m`
after every 2 is gone.

**Where to stop.** If `m` has a factor bigger than `sqrt(m)`, it also has one smaller than `sqrt(m)`,
which we would have found already. So once `d * d > m`, whatever is left is either 1 or a prime. That
limits the loop to about `sqrt(10^12) = 10^6` steps.

**Output.** Build a string. Before each factor, add `" * "` unless the string is still empty. Write the
factor as `f"{d}"` or `f"{d}^{e}"`. Finally print `f"{n} = {result}"`.

## Trace

Input `360`:

| d | m before | divides? | e | m after | result |
|---|---|---|---|---|---|
| 2 | 360 | yes | 3 | 45 | `2^3` |
| 3 | 45 | yes | 2 | 5 | `2^3 * 3^2` |
| 4 | 5 | (loop stops: 4 * 4 > 5) | | 5 | |
| leftover | 5 | m > 1 | | | `2^3 * 3^2 * 5` |

Output: `360 = 2^3 * 3^2 * 5`.

## Code

```python
n = int(input())

m = n               # what is left to factor
result = ""
d = 2
while d * d <= m:
    if m % d == 0:
        e = 0
        while m % d == 0:
            m //= d
            e += 1
        if result != "":
            result += " * "
        if e == 1:
            result += f"{d}"
        else:
            result += f"{d}^{e}"
    d += 1
if m > 1:
    # No divisor up to sqrt(m) is left, so m itself is prime.
    if result != "":
        result += " * "
    result += f"{m}"
print(f"{n} = {result}")
```

## Complexity

The outer loop runs at most `sqrt(n)` times (10^6 for `n = 10^12`), and the inner loop runs once per
prime factor counted (at most about 40 times in total). O(sqrt n) time, O(1) memory besides the output.

## Another way

**Try 2, then only odd divisors.** Handle `d = 2` separately, then start at 3 and step by 2. That halves
the work for large primes. You can go further and skip multiples of 3 as well (steps of 2 and 4
alternately: 5, 7, 11, 13, ...). These matter when time is tight; the simple version is clearer and
already fast enough here. For numbers much larger than 10^12 you would need entirely different methods
(Pollard's rho), which are beyond this course.

## Edge cases

- `n` prime: the loop finds nothing; the leftover is `n` itself: `13 = 13`.
- `n` a prime power: `1024 = 2^10`, `999966000289 = 999983^2` (needs `<=` in `d * d <= m`).
- `n = 2`: the loop does not run (`4 > 2`), leftover 2.
