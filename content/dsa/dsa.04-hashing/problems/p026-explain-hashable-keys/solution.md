The model answer is shown when you check. The ideas that must appear:

1. `d[[1, 2]]` raises a `TypeError` (the message mentions `unhashable type: 'list'`). A list is mutable, so its hash could change. A tuple is
   immutable, so its hash is fixed.
2. `d[(1, [2])]` also fails: a tuple is hashable only if **all** its items are hashable. The list inside makes it unhashable.
3. `1`, `1.0` and `True` are equal and have equal hashes, so they are the **same key**: `d[1.0]` and `d[True]` overwrite
   the value stored for `1`. The dictionary ends with 2 keys (`(1, 2)` and `1`). The rule: if `a == b` then `hash(a) == hash(b)`.
4. Insert a list key, then append to the list: its hash changes, but the entry sits in the bucket for the **old** hash.
   A lookup with the changed list probes the new bucket and does not find it.
5. Use a tuple `(row, col)`; use a `frozenset` (or a sorted string or tuple) for a set of letters.
