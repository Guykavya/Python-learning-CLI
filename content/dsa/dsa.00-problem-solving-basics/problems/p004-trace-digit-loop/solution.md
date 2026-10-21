## Walkthrough

First loop, starting with `n = 5207` and `step = 0`.

| Iteration | `n` at start | `step` | `digit = n % 10` | `n` after `// 10` | Printed |
|---|---|---|---|---|---|
| 1 | 5207 | 1 | 7 | 520 | `step 1 digit 7 left 520` |
| 2 | 520 | 2 | 0 | 52 | `step 2 digit 0 left 52` |
| 3 | 52 | 3 | 2 | 5 | `step 3 digit 2 left 5` |
| 4 | 5 | 4 | 5 | 0 | `step 4 digit 5 left 0` |

Now `n > 0` is false, the loop ends, and `done after 4 steps` is printed.

Second loop, starting with `m = 1000` and `zeros = 0`.

| Iteration | `m` at start | `m % 10` | `zeros` after | `m` after `//= 10` | Printed |
|---|---|---|---|---|---|
| 1 | 1000 | 0 | 1 | 100 | `m is now 100` |
| 2 | 100 | 0 | 2 | 10 | `m is now 10` |
| 3 | 10 | 0 | 3 | 1 | `m is now 1` |
| 4 | 1 | 1 | 3 | 0 | `m is now 0` |

Then `zeros: 3` is printed.

## Key idea

`n % 10` reads the last digit and `n // 10` removes it, so a `while n > 0` loop visits the digits from right
to left and runs once per digit. A zero digit is still a digit: it gets its own iteration (the `0` in `5207`,
and the three zeros in `1000`). Also watch the order of statements inside the loop: a value printed after
`n //= 10` is the *shortened* number.
