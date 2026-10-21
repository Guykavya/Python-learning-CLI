**How a dict finds a key.** A dict is a *hash table*: a block of slots. To store a key, Python
computes `hash(key)`, an integer, and uses it to choose a slot (roughly `hash % number_of_slots`).
To read the key later, it computes the hash again and goes straight to that slot. If two keys
land in the same slot (a collision) it tries other slots in a fixed pattern, and it confirms a
match with `==`. No scanning of all keys is needed, so lookup is O(1) on average.

**Hashable** means:

1. the object's hash **never changes** while it exists, and
2. objects that are equal (`==`) have **equal** hashes.

**What would go wrong with a list key.** Suppose `{[2, 5]: "Asha"}` were allowed. The entry is
placed in the slot chosen by `hash([2, 5])`, say slot 3. Now `key.append(1)`. The key object in
the table is now `[2, 5, 1]`.

- Looking up `[2, 5, 1]` computes a new hash, goes to a different slot, and finds nothing.
- Looking up `[2, 5]` goes to slot 3 and finds the entry, but its key `[2, 5, 1]` is not equal
  to `[2, 5]`, so no match.

The entry is still in the dict but can never be found again. Python avoids this broken state
by not giving mutable built-in types (list, dict, set) a hash at all.

**Why `(2, 5)` is safe.** A tuple cannot change, and ints cannot change, so the hash of
`(2, 5)` is fixed forever. A tuple's hash is built from its items' hashes, so `(2, [5])` is
not hashable: the list inside could change, and with it the tuple's value.

**A pair where order does not matter.** Use `frozenset({"Asha", "Ravi"})`. It is an
immutable set, so it is hashable, and `frozenset({"Ravi", "Asha"})` is equal to it. A sorted
tuple like `tuple(sorted(["Ravi", "Asha"]))` also works.

Key ideas to check: hash table and slots; O(1) lookup; the two hashability rules; a changed key
would be lost; tuples are hashable only if their items are; frozenset for unordered keys.
