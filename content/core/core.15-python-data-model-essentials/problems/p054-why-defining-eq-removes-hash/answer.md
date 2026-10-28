**1. What happens.** In `A`, writing `__eq__` makes Python set `A.__hash__ = None` automatically. So `hash(A(1))` raises `TypeError: unhashable type: 'A'` and an `A` object cannot go into a set or be a dict key. `B` defines nothing: it keeps the default `__eq__` (identity) and the default `__hash__` (based on identity), so two `B(1)` objects are different, and both can sit in a set (`len == 2`). In `C`, the subclass defines `__hash__` again, so hashing works (`len({C(1), C(1)}) == 1` because they are now equal **and** have equal hashes).

**2. Why Python does this.** The rule that must hold for hash tables: **if `a == b` then `hash(a) == hash(b)`**. A set or dict finds an object by its hash first, and only then compares with `==`. The default hash is built from identity. If you change what "equal" means but keep an identity-based hash, two objects you call equal would get different hashes and land in different buckets: `{A(1)}` would not "contain" `A(1)`, and a dict would hold duplicates that are equal. Python cannot know how to compute a consistent hash from your own `__eq__`, so it takes the safe choice: **not hashable**, a loud `TypeError` instead of silent wrong behaviour.

**3. Three ways to get hashing back.**

```python
class A:
    def __init__(self, n):
        self.n = n
    def __eq__(self, other):
        return isinstance(other, A) and self.n == other.n
    def __hash__(self):
        return hash(self.n)          # same fields as __eq__ uses
```

or `@dataclass(frozen=True)` (hash generated from the fields), or `@dataclass(unsafe_hash=True)` (you promise not to mutate). Only fields that `__eq__` compares may go into the hash.

**4. The trap.** The hash must not change while the object is in a set or dict. If you hash on a mutable field and then change it, the object is stored in the wrong bucket and can no longer be found. So hashable objects should be treated as immutable (or at least never mutate the fields that are hashed).
