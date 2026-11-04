# Prefix sums of an array

A **prefix sum** array `p` stores the running total of an array `a`. It has one more cell than `a`:

- `p[0] = 0` (the sum of nothing),
- `p[i] = a[0] + a[1] + ... + a[i-1]` for `i = 1 .. n`.

So `p[i]` is the sum of the first `i` elements. Build `p` with **one pass**: each new cell is the previous cell plus
one element. Print all `n + 1` values on one line, separated by spaces.

## Input

- Line 1: `n`.
- Line 2: `n` integers (an empty line when `n = 0`).

## Output

One line: `p[0] p[1] ... p[n]`.

## Example

Input:

```
5
3 -1 4 1 5
```

Output:

```
0 3 2 6 7 12
```

`p[3] = 3 + (-1) + 4 = 6`. The line has 6 numbers for 5 elements, and it starts with 0.

With `n = 0` (the second line is empty) the output is just `0`.

## Constraints

- `0 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`

Use `input()` without a prompt message.
