# Two single numbers

A list has `n` integers (`n` even). Two different values `a` and `b` appear **once**; every other value appears exactly twice.
Print `a` and `b`, smaller first.

The XOR of the whole list is `a ^ b`, but that mixes the two. Since `a != b`, `a ^ b` has at least one 1 bit. At that bit, `a` and
`b` differ. Use `low = x & -x` to pick the lowest such bit. Split all the numbers into those that have that bit and those that
don't: `a` and `b` land in different groups, and each pair of equal numbers lands together. XOR inside each group.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

One line: `a b` with `a < b`.

## Examples

| Input | Output | Why |
|---|---|---|
| `6` / `1 2 1 3 2 5` | `3 5` | XOR of all is `3 ^ 5 = 6`, lowest bit 2 |
| `2` / `7 4` | `4 7` | no pairs at all |
| `4` / `0 9 9 6` | `0 6` | one of the singles is 0 |

## Constraints

- `2 <= n <= 10^6`, `n` is even
- `0 <= value < 2^30`

Use `input()` without a prompt message.
