# Power with a loop

Read a whole number `a` (the base) and then a whole number `b` (the exponent).
Print `a` raised to the power `b`, that is, `a` multiplied by itself `b` times.

**Rule:** compute it with a loop. Do not use the `**` operator, do not call `pow()`, and do not import anything.

By definition, anything to the power 0 is 1. This includes `0` to the power `0`, which we also define as `1` here.

## Input

Two lines:

1. the base `a`
2. the exponent `b`

Use `input()` without a prompt message.

## Output

One line: the value of `a` to the power `b`, as a whole number (no `.0`).

## Examples

| Input | Output | Why |
|---|---|---|
| `2` then `10` | `1024` | 2 multiplied by itself 10 times |
| `-3` then `3` | `-27` | an odd number of negative factors stays negative |
| `-2` then `4` | `16` | an even number of negative factors is positive |
| `5` then `0` | `1` | anything to the power 0 is 1 |
| `0` then `0` | `1` | defined as 1 for this problem |

## Constraints

- `-100 <= a <= 100`
- `0 <= b <= 500`
- The answer can be hundreds of digits long. Python integers have no size limit, so that is fine.

## Before you code

Work out `3` to the power `4` by hand, one multiplication at a time, and write down the running result after each step.
Then write your plan as comments at the top of `solution.py`. What should the running result start at?
