## Approach

Translate the one-array loop back into the 2-D table. The 0/1 rule "each item at most once" lives in **which row** the "take" option reads. In one array, "which row" becomes "**has this cell been overwritten yet in this pass?**", and that is decided by the loop direction.

## Model answer

See `answer.md`.

## What to check

- You explained the direction with **the order of visits** (smaller index visited later when going down), not only with "it works".
- You traced the single-item example and got 10, 20, 30, which shows the item reused.
- You said the upward loop is not "wrong" in general: it is the **right** loop for the unbounded knapsack.
- You applied the rule to subset sum and counting, not only to knapsack.

## Another way

Prove it with a two-row version: `new = old[:]`, then `new[w] = max(old[w], old[w - wt] + val)` in **any** order. That is always 0/1, because every read is from `old`. The downward one-array loop is just a way to get the same reads without the copy. For the unbounded knapsack, read from `new` instead: `new[w] = max(old[w], new[w - wt] + val)`, which needs the upward order so that `new[w - wt]` is ready.
