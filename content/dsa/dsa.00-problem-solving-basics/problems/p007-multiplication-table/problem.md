# Multiplication table

Read an integer `n`, then a count `k`. Print the first `k` lines of the multiplication table of `n`.

Line `i` (for `i` from 1 to `k`) must look exactly like this:

```
n x i = p
```

where `p` is `n * i`. The `x` is a lowercase letter x, and there is exactly one space on each side of `x` and `=`.

## Input

Two lines:

1. the integer `n`
2. the integer `k`

## Output

Exactly `k` lines, in the format above, for `i = 1, 2, ..., k`.

## Examples

Input:

```
7
3
```

Output:

```
7 x 1 = 7
7 x 2 = 14
7 x 3 = 21
```

Input (negative `n`):

```
-4
2
```

Output:

```
-4 x 1 = -4
-4 x 2 = -8
```

Input (`n` is zero):

```
0
2
```

Output:

```
0 x 1 = 0
0 x 2 = 0
```

## Constraints

- `-1000 <= n <= 1000` (it may be negative or 0)
- `1 <= k <= 100`

Use `input()` without a prompt message.

## Before you code

Write the expected output for `n = 3`, `k = 4` by hand. Which parts of each line change and which stay the same?
Write your plan as comments at the top of `solution.py`.
