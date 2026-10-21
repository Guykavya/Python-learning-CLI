# Factorial

The factorial of `n`, written `n!`, is the product of all whole numbers from 1 to `n`:

```
5! = 1 * 2 * 3 * 4 * 5 = 120
```

By definition, `0! = 1` (an empty product is 1, just as an empty sum is 0).

Read `n` and print `n!`.

**Rule:** do not use `import`. In particular, no `math.factorial`. Build it with a loop.

## Input

One line with an integer `n`.

## Output

One line with a single integer: `n!`, written out in full.

## Examples

| Input | Output |
|---|---|
| `5` | `120` |
| `1` | `1` |
| `0` | `1` |
| `10` | `3628800` |

## Constraints

- `0 <= n <= 300`
- `300!` has 615 digits. Python integers grow as big as needed, so this is fine, but the answer must be exact.

Use `input()` without a prompt message.

## Before you code

Work `4!` by hand, writing the running product after each multiplication. What should the product start at?
Write your plan as comments at the top of `solution.py`.
