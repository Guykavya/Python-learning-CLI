## Walkthrough

| `x` | `range(2, x)` | `d` values tried | first divisor | `break`? | printed |
|---|---|---|---|---|---|
| 1 | empty | none | none | no | `1 is prime` |
| 2 | empty | none | none | no | `2 is prime` |
| 3 | 2 | 2 (3 % 2 = 1) | none | no | `3 is prime` |
| 4 | 2, 3 | 2 (4 % 2 = 0) | 2 | yes | `4 = 2 * 2` |
| 5 | 2, 3, 4 | 2, 3, 4 (no zero remainder) | none | no | `5 is prime` |
| 6 | 2..5 | 2 | 2 | yes | `6 = 2 * 3` |
| 7 | 2..6 | 2, 3, 4, 5, 6 | none | no | `7 is prime` |
| 8 | 2..7 | 2 | 2 | yes | `8 = 2 * 4` |
| 9 | 2..8 | 2 (rem 1), 3 (rem 0) | 3 | yes | `9 = 3 * 3` |
| 10 | 2..9 | 2 | 2 | yes | `10 = 2 * 5` |
| 11 | 2..10 | 2 to 10 | none | no | `11 is prime` |

Full output:

```
1 is prime
2 is prime
3 is prime
4 = 2 * 2
5 is prime
6 = 2 * 3
7 is prime
8 = 2 * 4
9 = 3 * 3
10 = 2 * 5
11 is prime
```

Note `8 = 2 * 4`, not `8 = 2 * 2 * 2`: the program prints only the first divisor and `x // d`.

## Key idea

- **for-else:** the `else` belongs to the inner `for` (same indentation). It runs when the loop runs out of values
  without a `break`. Here that means "no divisor was found", which is exactly "prime". It replaces a flag variable
  such as `is_prime = True`.
- **The 1 quirk:** for `x = 1`, `range(2, 1)` is empty. An empty loop never breaks, so the `else` runs and the
  program says `1 is prime`, which is false (a prime must be greater than 1). The same happens for `x = 2`, but
  there the answer happens to be right. The fix is to start at `range(2, 12)`, or to check `x < 2` separately.
- Edge cases hide in empty loops. Whenever a loop can run zero times, ask what the code after it does then.
