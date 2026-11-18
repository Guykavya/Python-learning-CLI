## Approach

The fast LIS is a DP with a cleverer state. Instead of "the LIS that ends at index `i`" (one value per index, `O(n)` work each to compute), it keeps "the best ending for each **length**". Three facts carry the whole explanation:

1. **Meaning**: `tails[k]` is the smallest last value of an increasing subsequence of length `k + 1`.
2. **Invariant**: `tails` is strictly increasing, so it can be binary searched.
3. **Update**: a new `x` improves exactly one length, the one found by `bisect_left`; everything else stays true.

## Model answer

See `answer.md`.

## What to check

- You defined `tails[k]` **precisely**, with "smallest" and "length `k + 1`". "The LIS so far" is wrong: `tails` is not a subsequence.
- You **argued** the sorted order (the "drop the last element" step), not only observed it on an example.
- You explained both cases of the update: append, and replace at the first entry `>= x`.
- You counted the work per number (`O(log n)`) and named what the `O(n^2)` DP does instead.

## Another way

A different picture is **patience sorting**: deal the numbers like cards onto piles, each card on the leftmost pile whose top card is `>=` it, or on a new pile at the right. The tops of the piles are exactly `tails`, and the number of piles is the LIS length. Keeping a parent pointer from each card to the top of the pile to its left (at the moment it is placed) lets you rebuild an actual LIS from the last pile. Try to explain the pile picture in four sentences and compare it with yours.
