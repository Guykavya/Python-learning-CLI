## Approach

The set remembers the **old** hash. After the mutation, a lookup with the new value computes a new hash and never finds the old slot; a lookup with the old value finds the slot but `==` fails because the stored object changed. The object is still in the set (iteration and `len` see it) but unreachable by lookup.

## Output

```text
True
False
False
False
1
[Tag('b')]
True
True 1
```

## Complexity

Not applicable.

## Another way

The fix in real code: make hashable objects immutable (`frozen=True` dataclass, tuples) or rebuild the set after changes: `s = {x for x in s}` (this computes fresh hashes).
