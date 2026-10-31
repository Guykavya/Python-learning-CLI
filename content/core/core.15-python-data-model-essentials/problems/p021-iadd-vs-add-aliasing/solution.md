## Approach

`+` builds a new object, so the other name keeps the old value. `+=` with an `__iadd__` that mutates and returns `self` changes the shared object, so every name sees the change. Without `__iadd__`, `+=` silently falls back to `+`.

## Output

```text
Bag([1, 2]) Bag([1]) False
Bag([1, 2]) Bag([1, 2]) True
[1, 2]
[1, 2, 3] [1, 2]
(1, 2) (1,)
3 1 False
None
```

## Complexity

Not applicable.

## Another way

Print `id(a)` before and after each statement: the id stays the same only for in-place changes.
