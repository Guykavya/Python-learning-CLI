# Count the set bits

The **popcount** of a number is how many 1-bits it has in binary. For example `13 = 1101` has popcount 3, and `0` has 0.

Write it with the bit trick: `n & (n - 1)` clears the **lowest** 1-bit of `n`. Repeat until `n` becomes 0 and count the
rounds. This does one round per 1-bit (not one per bit position).

(Python also has `bin(n).count("1")` and `int.bit_count()`. Use the trick here, so that you know it for a
language that does not have them.)

## Input

- Line 1: `q`.
- The next `q` lines: one integer `n` each.

## Output

`q` lines: the number of 1-bits of each `n`.

## Example

Input:

```
4
13
0
255
1024
```

Output:

```
3
0
8
1
```

`13 = 1101`, `255 = 11111111`, `1024 = 10000000000`.

## Constraints

- `1 <= q <= 50000`
- `0 <= n < 2^62`

Use `input()` without a prompt message. For many lines, reading all input at once
(`import sys` and `sys.stdin.read().split()`) is faster.
