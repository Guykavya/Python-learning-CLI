# Trailing zeros of n!

`n!` (n factorial) is `1 * 2 * 3 * ... * n`, and `0! = 1`. For example `10! = 3628800`, which
ends with **2** zeros.

Read `n` and print how many zeros `n!` ends with.

`n` can be as large as 10^18, so you cannot compute `n!` itself: it would have more digits than
there are atoms in your computer. You must count the zeros without building the number.

## Input

One line: the integer `n`. Use `input()` without a prompt message.

## Output

One line: the number of trailing zeros of `n!`.

## Examples

| Input | Output | Why |
|---|---|---|
| `5` | `1` | 5! = 120 |
| `10` | `2` | 10! = 3628800 |
| `4` | `0` | 4! = 24 |
| `0` | `0` | 0! = 1 |
| `25` | `6` | 25! = 15511210043330985984000000 |

## Constraints

- 0 <= n <= 10^18
- Your program must answer in well under a second, even for the largest `n`.

## Before you code

A trailing zero comes from a factor 10 = 2 * 5. Write out the factors of 10! by hand and count
the 2s and the 5s. Then ask: why does 25 give 6 and not 5? Write your plan as comments at the
top of `solution.py`.
