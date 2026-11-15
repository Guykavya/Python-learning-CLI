**1. The crash.** Every call of `power` waits for the call below it, so the waiting calls pile up on the **call stack**: `power(2, 1000000)`, `power(2, 999999)`, ... The **depth** of the stack equals `n`. Python stops at its **recursion limit** (about 1000 frames by default) and raises `RecursionError: maximum recursion depth exceeded`. The answer itself is fine; the problem is only the depth.

**2. Halving.** `fast_power` calls itself with `n // 2`: 1000000, 500000, 250000, 125000, 62500, ... 1, 0. The depth is about `log2(n) + 2`, which is 21 for a million. Doubling `n` adds only one level, so the depth grows **logarithmically**.

**3. One call, not two.** `half` is computed once and reused. Writing the call twice makes two calls per level, so the call tree doubles at every level: about `2^(log2 n) = n` calls in total, which throws away the gain (the depth is still small, but the work is `O(n)` again). With one call the work is `O(log n)` multiplications.

**4. Raising the limit.** It hides the real problem. A very deep Python stack can overflow the C stack and crash the whole interpreter (segmentation fault), it uses a lot of memory, and the algorithm still needs a million calls. Changing the algorithm (halving) or using a loop is the real fix.

Checklist: your answer should mention
- [ ] **recursion limit** / `RecursionError`
- [ ] the **depth** of the stack equals `n` for `power`
- [ ] **log** (log2 n) depth for `fast_power`, about 20 levels for a million
- [ ] computing `half` **once** (two calls would make `O(n)` calls)
- [ ] why `setrecursionlimit` is not a real fix
