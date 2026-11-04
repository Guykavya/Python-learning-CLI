**1. Which are correct?** `key1` (sorted letters) and `key2` (26 counts) are correct: two words share the key exactly when they have the same letters with the same
multiplicities. `key3` (sum of codes) is wrong: `ad` has `97 + 100 = 197` and `bc` has `98 + 99 = 197`, but they are not anagrams. `key4` (set of letters)
is wrong: `aab` and `ab` have the set `{a, b}`, yet `aab` has two `a`s. Keys must also distinguish by **counts**, and a sum throws away too much.

**2. Hashable.** `sorted(w)` returns a list. Lists are mutable and Python refuses to hash them (a dictionary could not trust a key that can change).
`"".join(sorted(w))` is a string: immutable, hashable, and still the same for all anagrams. A tuple would work too.

**3. Cost.** `key1` costs O(L log L) for the sort. `key2` costs O(L) to count plus O(26) to build the tuple. For long words on a small alphabet counting is faster;
for short words (a handful of letters) sorting is usually just as fast and simpler to write.

**4. Large alphabets.** A 26-tuple becomes a tuple with thousands of mostly zero entries, which is wasteful. Store only the letters that appear:
`tuple(sorted(Counter(w).items()))`, a sorted list of `(letter, count)` pairs.

**5. Same idea elsewhere.** Isomorphic strings: replace each letter by the order of its first appearance (`egg` and `add` both become `0 1 1`) and compare.
Any "group by canonical form" problem has this shape: choose a form that is equal exactly when the items are equivalent.
