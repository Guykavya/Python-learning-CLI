## Hint 1

Python's `set` and `dict` find objects in two steps: first the **hash** (which picks a bucket), then `==` among the objects in that bucket. What does the default `__hash__` use? What would happen to the first step for two objects that your `__eq__` says are equal?

## Hint 2

The contract is "equal objects have equal hashes" (the opposite is allowed: different objects may share a hash). A class that defines `__eq__` but not `__hash__` gets `__hash__ = None`. List the fixes: your own `__hash__`, `@dataclass(frozen=True)`, `unsafe_hash=True`. Then think about what happens to a hashed object whose field is changed later.

## Hint 3

Plan of the answer:

```text
1. A: __eq__ without __hash__ -> __hash__ = None -> unhashable; B: defaults (identity) -> hashable; C: defines __hash__ -> hashable
2. a == b  =>  hash(a) == hash(b); otherwise equal objects land in different buckets; set/dict break; Python chooses a TypeError
3. def __hash__(self): return hash(self.n)  # same fields as __eq__; frozen dataclass; unsafe_hash
4. mutate a hashed field -> object is in the wrong bucket -> lookup fails ("lost" in the set)
```
