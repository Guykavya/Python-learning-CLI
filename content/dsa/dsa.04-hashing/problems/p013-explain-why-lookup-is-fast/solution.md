The model answer is shown when you check. The ideas that must appear:

1. A failed list lookup compares `x` with all `n` items, so 100000 checks do about 10^10 comparisons.
2. A set computes `hash(x)`, uses it to pick a slot, and only compares `x` with the few items in that slot.
3. Worst case is O(n) when many items collide in one slot; with a good hash and a table that resizes, collisions are
   rare and the average is O(1).
4. Costs: more memory (spare empty slots), no positions or sorted order, and building the table is slower than building a list.
5. The value must be hashable (immutable with a stable hash, equal values with equal hashes), or the stored item
   could not be found again.
