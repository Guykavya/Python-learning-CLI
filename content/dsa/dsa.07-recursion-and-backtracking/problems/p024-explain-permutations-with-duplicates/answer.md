**1. Six results.** The plain version treats the two 1s as different items (they sit at different positions), so it builds all `3! = 6` orderings of 1a, 1b, 2. Swapping 1a and 1b gives the same list of values, so only `6 / 2 = 3` are different: `[1, 1, 2]`, `[1, 2, 1]`, `[2, 1, 1]`.

**2. Sorted.** The rule compares an item only with its **previous** neighbour `nums[i - 1]`. Sorting puts equal values next to each other, so every group of equal values is a run in the list and "the previous equal value" is always the left neighbour.

**3. The rule.** A copy of a value may be chosen only if the copy just before it is **already used**, that is, already earlier in the path. So 1b can be placed only after 1a: equal values always appear in their **original (sorted) order**, 1a before 1b. The branch "1b first while 1a is still free" is cut at once. Among the orderings that differ only by swapping equal copies, exactly one has the copies in sorted order, so each distinct permutation is built once. When the previous copy is free, choosing this copy would only repeat a sub-tree that the previous copy already explored at this level.

**4. Better than a set.** A set removes duplicates only **after** they were built. For `[1] * 10` the plain version builds `10! = 3,628,800` lists to keep one. With the rule, at every level only the first free 1 is allowed, so the tree is a single chain of 11 calls.

Checklist: your answer should mention
- [ ] the 1s are at different positions, so 6 orderings but 3 distinct
- [ ] **sorted** so that equal values are neighbours
- [ ] `not used[i - 1]`: the **previous** equal copy must already be **used** (copies stay in order)
- [ ] the rule cuts branches **before** they are built (pruning), unlike a `set` afterwards
- [ ] the numbers for `[1] * 10`: 3,628,800 against one result
