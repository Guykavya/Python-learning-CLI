# Peak of a mountain (interactive)

A hidden array `a` of length `n` is a **mountain**: it strictly increases up to a peak position `p` and then strictly decreases (`0 < p < n - 1`).
Find `p` (the 0-based index of the peak).

Interactive rules, as in the first-bad-version problem:

- The test first sends one line: `n`.
- To read element `i`, print `? i` with `flush=True`; the reply is one line with `a[i]`.
- When you know `p`, print `! p` (flush) and stop.

You may ask at most `2 * bit_length(n) + 4` questions. For `n = 10^9` that is 64. A scan is impossible.

## Constraints

- `3 <= n <= 10^9`

## Example

```
7                  <- sent by the test; hidden array 1 3 8 12 9 5 2
? 3                <- you
12                 <- reply
? 4                <- you
9                  <- reply
...
! 3                <- you
```
