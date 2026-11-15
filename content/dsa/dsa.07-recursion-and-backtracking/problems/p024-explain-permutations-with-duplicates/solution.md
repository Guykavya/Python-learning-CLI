## Approach

Think of equal values as labelled copies. The plain algorithm produces every arrangement of the labels; the skip rule keeps exactly one representative per group, the one where the copies appear in their sorted order. Sorting is needed so the copies are neighbours and "the previous copy" is `nums[i - 1]`.

## Model answer

See `answer.md` and tick the checklist at its end.

## What to check

- You explain the rule in terms of the **previous copy being used**, not only "skip duplicates".
- You see that `used[i - 1]` (the other way round) would also work, by keeping the reverse order of copies, but with more dead branches; the usual form is `not used[i - 1]`.
- You compare cost: pruning while building against filtering afterwards.

## Another way

Count each value (`{1: 2, 2: 1}`) and at each level choose a **value** whose count is still positive, decreasing and restoring the count. Distinct values are tried once per level, so no duplicates can appear and no sorting is needed.
