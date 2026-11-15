**1. Possible answers.** If the `n` values are distinct, the input can be arranged in `n!` ways. The algorithm must produce the right sorted output for each, so it must be able to tell all `n!` situations apart.

**2. One comparison.** A comparison has two outcomes (less or not). After `k` comparisons the algorithm can distinguish at most `2^k` situations: its decisions form a binary tree of depth `k` with at most `2^k` leaves.

**3. The bound.** We need `2^k >= n!`, so `k >= log2(n!)`. Since `n!` is at least `(n/2)^(n/2)`, `log2(n!)` is at least `(n/2) log2(n/2)`, which is of order `n log n`. For `n = 4`: `4! = 24`, but 4 comparisons give only `2^4 = 16` outcomes, so at least 5 comparisons are needed.

**4. The escape.** Counting sort never asks 'is a < b?'. It uses each value as an index into an array. That works only because the values are integers in a small known range `0..k`; the work is `O(n + k)`. Radix sort sorts big integers by repeating this on each digit.

**5. When to use what.** Counting or radix sort beat merge sort when keys are small or fixed-width integers (exam marks 0..100, ages, 32-bit ids). They cannot be used for arbitrary objects with only a comparison (names with custom order), for floats with huge ranges, or when the range `k` is much larger than `n`.
