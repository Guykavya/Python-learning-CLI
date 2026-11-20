## Model answer

**1. Nodes versus indices.** Every internal node splits its range in two, so there are `n` leaves and `n - 1` internal nodes: `2n - 1` nodes. But heap numbering gives a node the index `2i` or `2i + 1` of its parent **whether or not the other positions on that level are used**. When the tree is lopsided, some branches stop early (they reach a leaf) while others go one level deeper, and the indices of that deepest level are spread out with gaps. The list must reach the largest index, not just hold `2n - 1` values.

**2. Height.** Each level halves the range length (rounding up on one side), so after `h` levels the longest range has length `ceil(n / 2**h)`. The leaves are reached when that is 1, which first happens at `h = ceil(log2(n))`.

**3. The bound.** On level `h` (the root is level 0) the indices are `2**h .. 2**(h + 1) - 1`. So the largest index is less than `2**(h + 1)`. With `h = ceil(log2(n))` we have `2**h < 2n` (because `2**(h - 1) < n`), so the largest index is below `2 * 2**h < 4n`.

**4. Powers of two.** If `n = 2**k`, the tree is perfect: height `k`, and the bottom level is exactly indices `n .. 2n - 1`. So `2n` is enough. For `n = 9`, the height is `ceil(log2 9) = 4`, so the bottom level can reach index `2**5 - 1 = 31`, almost `4 * 9 = 36`; the output shows 31. The worst case is just above a power of two, like `n = 1025` (index 4095 against `4n = 4100`).

**5. The iterative tree.** It does not insist that node `i` covers a contiguous range split at the midpoint. It puts the leaves at `n .. 2n - 1` directly and builds parents from children, so the indices are exactly `1 .. 2n - 1`. The price is that for `n` not a power of two some internal nodes join non-neighbouring pieces; the query never uses them.

**Checklist: your answer should mention**
- [ ] `2n - 1` nodes but **indices with gaps** (heap numbering of a lopsided tree)
- [ ] the **height** is `ceil(log2 n)`
- [ ] level `h` uses indices up to `2**(h + 1) - 1`, and `2**h < 2n`, so the maximum is below `4n`
- [ ] a **power of two** gives a perfect tree that fits in `2n`
- [ ] the bad cases are just above a power of two (`n = 9`, `n = 1025`)
- [ ] the iterative tree puts leaves at `n .. 2n - 1` and needs exactly `2n`
