## Model answer

**1. The 2-D table.** "Take item `i`" is `f[i-1][w - wt[i]] + val[i]`: it reads the row **above**, the best value using only the items **before** `i`. Item `i` is not in that row, so it can be added once and only once.

**2. The 1-D array.** The array is one row, overwritten in place, so `g[w - wt[i]]` is either still the old row (items before `i`) or already the new row (it may include item `i`). Going **downwards**, `w - wt[i]` is smaller than `w`, so it is visited **later** in this pass: when `g[w]` reads it, it is still old, exactly like `f[i-1][...]`. Going **upwards**, `w - wt[i]` was visited **earlier** in the same pass, so it has already been updated for item `i`.

**3. What the upward loop computes.** With the single item (2, 10): `g[2] = g[0] + 10 = 10`, then `g[4] = g[2] + 10 = 20` (reads the cell just updated), then `g[6] = g[4] + 10 = 30`, and `g[7] = g[5] + 10 = 30`. The same item was used three times. Downwards, every read is of a cell that is still 0, so `g[7] = 10`: the item once. So the upward loop solves the **unbounded** knapsack: each item may be reused.

**4. Which belongs where.** 0/1 knapsack (each item at most once): capacity **high to low**. Unbounded knapsack (unlimited copies): **low to high**. For the unbounded problem, reading a value that already includes item `i` is exactly what we want: `g[w - wt]` may contain some copies of item `i`, and we add one more.

**5. Subset sum and counting.** Each number may be used **once**, so they are 0/1 problems: loop `s` from high to low. Upwards, `[2]` with target 4 would be reachable (2 + 2), and the counts would count multisets instead of subsets.

**Checklist: your answer should mention**
- [ ] the "take" option of the 2-D table reads the **previous row** (items before `i` only)
- [ ] the 1-D array is that row **overwritten in place**, so the question is old value vs new value
- [ ] **backwards** (high to low): `g[w - wt]` is smaller, visited later, so still the **old** value
- [ ] forwards (low to high): `g[w - wt]` already includes the current item, so it allows **reuse**
- [ ] the trace `g[2] = 10, g[4] = 20, g[6] = 30`: the **same item twice** (and three times)
- [ ] 0/1 = backwards, unbounded = forwards, and reuse is *wanted* in the unbounded case
- [ ] subset sum and counting subsets are 0/1 problems, so they also loop backwards
