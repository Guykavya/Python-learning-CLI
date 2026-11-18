## Model answer

**1. Meaning.** After reading some prefix of `nums`, `tails[k]` is the **smallest possible last value** of a strictly increasing subsequence of **length `k + 1`** among the numbers read so far. A smaller last value is always at least as good, because every number that can extend a subsequence ending in a big value can also extend one ending in a smaller value.

**2. Sorted.** Suppose `tails[k] >= tails[k + 1]`. Take an increasing subsequence of length `k + 2` that ends in `tails[k + 1]` and drop its last element. What is left has length `k + 1` and ends in a number smaller than `tails[k + 1]` (the subsequence is strictly increasing), and `tails[k + 1] <= tails[k]`, so it ends in a number smaller than `tails[k]`. That contradicts "`tails[k]` is the smallest last value for length `k + 1`". So `tails[k] < tails[k + 1]`: the list is strictly increasing, which is what makes binary search possible.

**3. Replace.** `bisect_left` gives the first `k` with `tails[k] >= x`. If `k > 0`, then `tails[k - 1] < x`, so `x` extends the length-`k` subsequence ending in `tails[k - 1]`: we get a length-`k + 1` subsequence ending in `x` (if `k = 0`, `x` alone has length 1). Since `x <= tails[k]`, `x` is a last value at least as small, so `tails[k] = x` keeps the meaning of question 1. `x` cannot improve any other length: it cannot extend a length-`k + 1` subsequence (`tails[k] >= x`), and for shorter lengths the entries are already smaller than `x`. The order stays sorted: `tails[k - 1] < x <= tails[k] < tails[k + 1]`. If `k == len(tails)`, `x` is larger than every entry and extends the longest one: append.

**4. Length.** By the meaning in question 1, `tails` has an entry for length `L` exactly when some increasing subsequence of length `L` exists. So after all numbers, `len(tails)` is the longest length that exists: the LIS.

**5. Not a subsequence.** For `[3, 4, 1]`, `tails = [1, 4]`, but `1` comes **after** `4` in the input, so `[1, 4]` is not a subsequence. Each entry is the best ending for **its own length**, possibly from a different subsequence. Only the **length** of `tails` is meaningful; to rebuild an actual LIS you need extra parent pointers (or the `O(n^2)` table of section 13).

**6. Cost.** Each of the `n` numbers does one binary search on a sorted list of at most `n` entries, `O(log n)`, plus one append or one assignment, `O(1)`. Total `O(n log n)` time and `O(n)` memory. The `O(n^2)` DP spends its time scanning **every** earlier index `j` for each `i`; `tails` keeps only the one best candidate per length, in sorted order, so a binary search replaces that scan.

**7. Non-decreasing.** Use `bisect_right`. An equal number may now **extend** a subsequence that ends in the same value, so `x` should go after the entries equal to it, not replace the first of them. With `bisect_left`, `[2, 2, 2]` gives 1; with `bisect_right` it gives 3.

**Checklist: your answer should mention**
- [ ] `tails[k]` = the **smallest last value** of an increasing subsequence of length `k + 1` so far
- [ ] why smallest: a smaller ending can be extended by more numbers
- [ ] `tails` is strictly increasing, with the "drop the last element" argument
- [ ] `bisect_left` finds the first entry `>= x`; `tails[k - 1] < x` so `x` extends length `k`
- [ ] replacing keeps the meaning (and the sorted order); append when `x` beats every entry
- [ ] `len(tails)` is the LIS length, but `tails` itself is **not** a subsequence (`[3, 4, 1]` gives `[1, 4]`)
- [ ] `n` numbers times `O(log n)` binary search = `O(n log n)`; the `O(n^2)` DP scans every earlier `j`
- [ ] `bisect_right` for non-decreasing
