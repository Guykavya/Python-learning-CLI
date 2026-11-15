# Kth of two sorted arrays (interactive)

Two hidden arrays `A` (length `n`) and `B` (length `m`) are each sorted in non-decreasing order. Find the **k-th smallest** element of all `n + m` values together (duplicates count separately, `k = 1` is the minimum).
Lengths go up to `10^9`, so you cannot read the arrays. This is a classic challenge: the answer is found by binary searching **how many elements come from `A`**.

Interactive rules:

- The test first sends one line: `n m k`.
- To read `A[i]` print `? A i`; to read `B[j]` print `? B j` (both with `flush=True`). The reply is one line with the value. Indices are 0-based and must be inside the array.
- Print `! value` when you know the answer, then stop.

You may ask at most `4 * bit_length(max(n, m)) + 8` questions.

## Idea

If `i` elements of the answer's prefix (the `k` smallest) come from `A`, then `k - i` come from `B`. The split is right when `A[i - 1] <= B[k - i]` and `B[k - i - 1] <= A[i]`. As `i` grows, `A[i]` grows and `B[k - i - 1]` shrinks, so "`A[i] >= B[k - i - 1]`" is False...False True...True in `i`. Search the first True with `i` in `[max(0, k - m), min(k, n)]`. At the end the answer is the larger of `A[i - 1]` and `B[k - i - 1]` (those that exist).

## Example

```
3 3 4            <- n = 3, m = 3, k = 4; hidden A = 1 3 5, B = 2 4 6
? A 1            <- you
3                <- reply
...
! 4              <- the 4th smallest of 1 2 3 4 5 6
```
