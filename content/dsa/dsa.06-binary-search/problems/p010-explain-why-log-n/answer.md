**1. Counting.** Every probe halves the number of candidates. After `k` probes at most `n / 2^k` candidates remain, so we stop when `2^k >= n`, i.e. `k = ceil(log2 n)`.
Since `2^20 = 1,048,576`, a million elements need about 20 probes. A billion needs 30, because `2^30` is about 10^9.

**2. Doubling.** A list twice as large needs just one more probe: the first probe cuts it back to the old size.

**3. The precondition.** On `[5, 1, 4, 2, 3]` looking for 1: the middle is 4, and 1 < 4, so we go left and only see `[5, 1]`... that happens to work here, but look for 3: the middle is 4, 3 < 4 so we go left to `[5, 1]` and never see the 3 at the end. The result is "not found" although 3 is present. The discard step is only valid if everything on one side of the middle is smaller and everything on the other side is larger.

**4. Is it worth it?** For one query a linear scan costs `O(n)`. Sorting first costs `O(n log n)`, which is more, so for a single query do not sort. For `q` queries the scan costs `O(q * n)` and sort plus search costs `O(n log n + q log n)`, which wins as soon as `q` is larger than about `log n`.

**5. One step.** On a sorted list one comparison `a[mid] < x` tells us about all elements at once: everything at or before `mid` is `<= a[mid] < x`, so none of them can equal `x` and half the list is gone.
