# Reverse parts of an array in place

Reverse a part of an array **in place** with two pointers: `i` starts at the left end of the part, `j` at the right
end. Swap `a[i]` and `a[j]`, move `i` right and `j` left, and stop when they meet or cross. No second list is needed.

You get an array and `q` operations. Each operation `l r` reverses the part from position `l` to position `r`
(1-based, inclusive). Apply them in order and print the final array.

Write the two-pointer loop yourself. (Slicing with `[::-1]` also gives the right output, but the point is to learn
the swap loop you will reuse in many later problems.)

## Input

- Line 1: `n`.
- Line 2: `n` integers.
- Line 3: `q`.
- Next `q` lines: `l r`.

## Output

One line: the final array, separated by spaces.

## Example

Input:

```
7
1 2 3 4 5 6 7
3
1 7
1 3
4 7
```

Output:

```
5 6 7 1 2 3 4
```

Reversing everything gives `7 6 5 4 3 2 1`. Reversing the first 3 gives `5 6 7 4 3 2 1`. Reversing positions 4..7
gives `5 6 7 1 2 3 4`. These three reversals rotated the array to the right by 3, a classic trick.

## Constraints

- `1 <= n <= 200000`, `1 <= q <= 20`
- `1 <= l <= r <= n`
