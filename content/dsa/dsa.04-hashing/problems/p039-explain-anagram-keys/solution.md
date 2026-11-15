The model answer is shown when you check. The ideas that must appear:

1. `key1` and `key2` are correct. `key3` is wrong: `ad` and `bc` both sum to 101 (97 + 100 = 98 + 99). `key4` is wrong: `aab` and `ab` have the same
   set of letters but are not anagrams.
2. A list is mutable and unhashable; the joined string is immutable and hashable.
3. `key1` costs O(L log L); `key2` costs O(L + 26). Counting wins for long words over a small alphabet; sorting is simpler and fine for short words.
4. Use `tuple(sorted(Counter(w).items()))`, only the letters that appear, in a fixed order.
5. Isomorphic strings (replace each letter by the order of its first appearance), grouping by `i % k`, or any "canonical form" problem.
