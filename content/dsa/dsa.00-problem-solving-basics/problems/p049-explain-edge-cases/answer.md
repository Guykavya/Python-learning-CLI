**1. Edge cases and expected behaviour**

| Input | Correct output / behaviour |
|---|---|
| `n = 0` (no values) | There is no average, largest or smallest. The statement is silent, so pick a rule and state it, for example print `no data`. It must not crash. |
| `n = 1`, value `7` | `7.00`, `7`, `7` (the one value is the average, the largest and the smallest). |
| `n = 3`, values `-4 -9 -1` | `-4.67`, `-1`, `-9`. |
| `n = 4`, values `5 5 5 5` | `5.00`, `5`, `5`. |
| `n = 2`, values `10**18` and `10**18` | average `1000000000000000000.00`, largest and smallest `1000000000000000000`. Python ints do not overflow, but `total / n` is a float, which loses precision for huge totals; `total // n` plus the remainder would be exact. |
| `n = 3`, values `0 -3 8` (a mix including zero) | `1.67`, `8`, `-3`. |
| `n = -2` | Invalid input. `range(-2)` is empty, so treat it like `n = 0` or print an error; never divide. |
| `n = 2`, values `1 2` | `1.50`, shows that `/` (not `//`) is needed. |

**2. What breaks the first attempt**

- `n = 0`: the loop never runs, then `total / n` raises `ZeroDivisionError` and the program crashes.
- `n = -2`: no crash, which is worse. `range(-2)` is empty, so the division is `0 / -2`, printing
  `-0.00`, and largest/smallest print `0` although no numbers were read. Wrong, silently.
- All negative (`-4 -9 -1`): `largest` starts at 0 and no value is bigger, so it prints `0`, a number
  that is not even in the input.
- All positive (`3 4 9`): `smallest` stays 0 for the same reason. So the "it works" example only
  worked because it happened to contain both a positive and a negative value.
- `n = 1` with value `-5`: largest prints `0` instead of `-5`.

The fix: set `largest` and `smallest` to the first value read (or use a flag `first`), and handle
`n <= 0` before dividing.

**3. Choosing test inputs**

Start from the limits in the statement. If `n` can be 0..1000, test 0, 1, 2 and 1000. Those are the
boundaries, where loops run zero times, once, or the most times. For values, test the smallest and
largest allowed, zero, and negatives. Then test "just inside / just outside": if a rule changes at
100, test 99, 100 and 101. Add special shapes: all equal, already sorted, reverse sorted, the answer
at the very first or very last position. Finally, compute expected outputs by hand **before** running
the code, so the program cannot persuade you.

**4. Checklist**

1. Empty input (`n = 0`) and invalid counts.
2. Exactly one item.
3. All items equal.
4. All negative, and zero included.
5. Largest allowed values (overflow, float precision, speed).
6. Boundaries: just below, at, and just above each limit.
7. Answer at the first and at the last position.
8. Exact output format (decimals, spaces, capitals).

Key ideas to check: n = 0 causes ZeroDivisionError; initialising max/min to 0 is wrong for all-negative or all-positive data (initialise from the first value); n = 1 and all-equal cases; very large values; negative n is invalid input; boundaries and just-inside/just-outside values; work out expected output before running; a reusable checklist.
