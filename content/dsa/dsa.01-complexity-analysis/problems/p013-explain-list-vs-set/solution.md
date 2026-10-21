The model answer is shown when you check. The ideas that must appear:

1. `x in list` compares element by element and must check all of them when `x` is missing: O(n). The table grows
   about 10 times when the size does.
2. With a list the program does `m` scans of up to `n` items: O(n * m), up to 2 * 10^10 comparisons here.
3. A set computes the hash of the value and looks in one slot: O(1) on average, independent of size. Building it
   is O(n), so the program is O(n + m).
4. Lists keep order, duplicates and positions; sets need hashable values and keep no order. Set lookups are O(1)
   on average, not guaranteed in the worst case.
