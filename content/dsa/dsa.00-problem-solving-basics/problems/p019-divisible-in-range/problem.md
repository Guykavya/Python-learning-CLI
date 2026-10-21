# Count multiples in a range

Read three whole numbers `a`, `b` and `k`. Count how many integers `x` with `a <= x <= b`
are divisible by `k` (that is, `x % k == 0`), and print that count.

Both ends are **included**: if `a` or `b` is itself divisible by `k`, it counts.
Zero is divisible by every `k`, and negative numbers can be divisible too (`-6` is divisible by `3`).

## Input

Three lines:

1. `a`, the start of the range
2. `b`, the end of the range
3. `k`, the divisor

Use `input()` without a prompt message.

## Output

One line: the count, as a whole number.

## Examples

| a | b | k | Output | Why |
|---|---|---|---|---|
| `1` | `10` | `3` | `3` | 3, 6, 9 |
| `3` | `9` | `3` | `3` | 3, 6, 9: both ends count |
| `-6` | `6` | `3` | `5` | -6, -3, 0, 3, 6 |
| `7` | `7` | `2` | `0` | the range is just 7, which is odd |
| `4` | `8` | `1` | `5` | every number is divisible by 1 |

## Constraints

- `-1000000 <= a <= b <= 1000000`
- `1 <= k <= 1000000`

## Before you code

Work the `-6`, `6`, `3` example by hand, listing every number in the range and marking the multiples.
Then write your plan as comments at the top of `solution.py`. Which `range(...)` call covers `a` to `b` **including** `b`?
