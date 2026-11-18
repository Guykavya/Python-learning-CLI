## Hint 1

Run the chapter's printing version on `[10, 9, 2, 5, 3, 7, 101, 18]` and look at each line. After `x = 3`, `tails = [2, 3]`. Find, in the numbers read so far (`10, 9, 2, 5, 3`), an increasing subsequence of length 2 that ends in 3. Is there one of length 2 that ends in something smaller? That is the meaning of `tails[1]`.

## Hint 2

For question 2, take an increasing subsequence of length `k + 2` that ends in `tails[k + 1]`. Drop its last element. You now have one of length `k + 1`, and its last element is **smaller** than `tails[k + 1]`. Compare that with the definition of `tails[k]` (the smallest possible last value).

## Hint 3

For question 3: `bisect_left` returns the first `k` with `tails[k] >= x`, so `tails[k - 1] < x` (if `k > 0`). Put `x` after the length-`k` subsequence that ends in `tails[k - 1]`: that is a length-`k + 1` subsequence ending in `x`, and `x <= tails[k]`, so it is at least as good. Then check the sorted order around position `k`: `tails[k - 1] < x <= tails[k] < tails[k + 1]`.
