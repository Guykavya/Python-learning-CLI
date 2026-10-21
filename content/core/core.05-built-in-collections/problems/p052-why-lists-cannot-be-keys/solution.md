See the model answer shown when you check. The ideas that must appear:


1. A dict is a hash table. It computes `hash(key)` and uses that number to jump straight to a
   slot, so lookup is O(1) on average. Equal hashes are confirmed with `==`.
2. Hashable: the hash never changes during the object's life, and equal objects have equal hashes.
3. If a list key changed after being stored, its new hash would point to a different slot, and
   the stored entry would no longer be equal to the old value either. The entry would be lost
   inside the table. Python prevents this by refusing to hash lists.
4. A tuple of ints cannot change, so its hash is fixed. A tuple holding a list could change
   through the list, so it is not hashable.
5. `frozenset({"Asha", "Ravi"})`, or a sorted tuple such as `("Asha", "Ravi")`.
