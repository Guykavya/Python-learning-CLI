**1. Cost formula.** Every shift moves one larger value to the right of `key`, which removes exactly one inversion (a pair `i < j` with `a[i] > a[j]`).
A sorted list has no inversions, so the number of shifts equals the number of inversions `I`. The outer loop runs `n - 1` times. Total time is `O(n + I)`.

**2. Sorted input.** `[1, 2, 3, 4, 5]` needs 0 shifts. For each key the first comparison `a[j] > key` is false, so the while loop stops immediately. Only the 4 outer steps remain.

**3. Nearly sorted.** `[1, 2, 4, 3, 5, 6, 8, 7, 9, 10]` has `I = 2` (the pairs 4,3 and 8,7). Insertion sort does 2 shifts and about 9 outer steps, around 11 steps in all, while a random list of 10 numbers needs about 22.

**4. Reverse input.** Every pair is an inversion, so `I = n(n-1)/2`. This is the maximum, so it is the worst case: `O(n^2)`.

**5. Practical use.** For very small pieces the plain loop has almost no overhead (no recursion, no extra lists) and works on data already in the cache. Timsort uses it (with binary search) for short runs; introsort-style quicksorts switch to it for pieces of about 16 items.
