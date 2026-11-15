# Search in an array of unknown size (interactive)

A hidden **sorted** array `a` (strictly increasing integers) has an unknown length `n`. You can only ask for elements:

- The test first sends one line: the target `t`.
- To read element `i`, print `? i` with `flush=True`. The reply is `a[i]`, or the number `2147483647` if `i >= n` (past the end). Indices must be `>= 0`.
- When you know the answer print `! index` (the 0-based index of `t`) or `! -1` if `t` is not in the array, then stop.

All real values are smaller than `2147483647`, so that number always means "past the end".
You cannot start a binary search without `hi`. First find a bound by **doubling** (try index 1, 2, 4, 8, ...) until the value at that index is `>= t` (or past the end), then binary search between the last two indices.
You may ask at most `2 * bit_length(n) + 6` questions, with `n` up to `10^9`.

## Example

```
5              <- sent by the test: target t = 5
? 0            <- you
3              <- reply: a[0] = 3
? 1
7
...
! -1           <- you, when you are sure that 5 is not in the array
```

(In this example the array could be `3 7 9`.)
