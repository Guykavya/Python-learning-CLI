The model answer is shown when you check. The ideas that must appear:

1. Average chain length is `alpha = n / m`; a lookup costs about `1 + alpha` steps (one for the hash, `alpha` for the chain).
2. With `10^6` keys in 16 buckets each chain is about 62500 long: the table behaves like a list, O(n).
3. Doubling copies `1 + 2 + 4 + ... < 2n` keys in total, so inserts cost O(1) amortised. Growing by one copies `1 + 2 + ... + n`
   which is O(n^2).
4. In open addressing every key occupies a slot; clusters grow quickly as the table fills, and at load factor 1 a missing key
   is never answered by an empty slot (the search would loop). So keep the load factor below about 0.5 to 0.7.
5. Emptying a slot in the middle of a probe run would cut the run, and later keys would become unreachable. Use tombstones
   (a "deleted" marker), or shift later items back.
