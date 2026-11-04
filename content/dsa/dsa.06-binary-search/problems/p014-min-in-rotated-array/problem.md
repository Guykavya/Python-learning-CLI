# Minimum in a rotated sorted array (interactive)

A hidden array of `n` **distinct** numbers was sorted in increasing order and then rotated: for example `[11, 13, 15, 2, 4, 7]` (the sorted array `[2, 4, 7, 11, 13, 15]` rotated by 3). A rotation by 0 leaves it sorted.
Find the **smallest value**.

You cannot see the array. This is an interactive problem:

- The test first sends one line: `n`.
- To read element `i` (0-based) print `? i` with `flush=True`. The reply is one line with `a[i]`.
- When you know the minimum value, print `! value` (with flush) and stop.

You may ask at most `2 * bit_length(n) + 4` questions (about `2 log2 n`). For `n = 10^6` that is 44, far fewer than `n`.

## Constraints

- `1 <= n <= 10^6`, all values distinct and at least 1.

## Example

```
6              <- sent by the test (hidden array: 11 13 15 2 4 7)
? 2            <- you
15             <- reply
? 5            <- you
7              <- reply
...
! 2            <- you, when you are sure
```
