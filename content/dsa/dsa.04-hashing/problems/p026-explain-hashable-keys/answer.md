**1. Lists.** `d[[1, 2]] = "list"` raises a `TypeError` (the message mentions `unhashable type: 'list'`). A dictionary finds a key by its hash,
and the hash must never change while the key is stored. A list can be changed (`append`, item assignment), so its
content, and therefore any hash computed from it, can change. Python refuses to hash lists. The tuple `(1, 2)` cannot
change, so it has one fixed hash and is allowed.

**2. A tuple holding a list.** `d[(1, [2])]` fails with a `TypeError` too. The hash of a tuple is built from the
hashes of its items, so a tuple is hashable only if every item is. The inner list is not, so the whole tuple is not.
"Immutable container" is not enough; its contents must be hashable too.

**3. Equal keys.** `1 == 1.0` and `1 == True`, and equal numbers have equal hashes (`hash(1) == hash(1.0) == hash(True) == 1`).
The dictionary sees `1.0` and `True` as the same key as `1`, so those assignments only overwrite the value. The dictionary
ends with two keys: `(1, 2)` and `1`, so `len(d)` is 2 (the failing lines do not add anything). The rule is: if `a == b` then
`hash(a) == hash(b)`.

**4. If lists were allowed.** `k = [1, 2]; d[k] = "x"` stores the entry in the bucket chosen by the hash of `[1, 2]`.
Then `k.append(3)` changes the hash. `d[k]` now looks in the bucket for `[1, 2, 3]` and finds nothing, although the entry
is still inside the dictionary. It is lost (and also appears under a stale hash).

**5. Your own data.** A `(row, col)` tuple of two ints is a perfect key. For "a set of letters" use a `frozenset(letters)`,
or a sorted string such as `"".join(sorted(letters))` (the anagram key from this module).
