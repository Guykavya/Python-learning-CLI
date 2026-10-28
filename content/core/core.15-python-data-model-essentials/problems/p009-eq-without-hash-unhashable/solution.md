## Approach

The rule is applied per class body: a class body that has `__eq__` but not `__hash__` sets `__hash__ = None`. Inheritance does not rescue it, which is why `S` is unhashable even though `Q` has a hash.

## Output

```text
None
True True
error: unhashable type: 'P'
error: P cannot be a dict key
2 True
False True
error: S cannot be a set element
```

## Complexity

Not applicable.

## Another way

Print `P.__dict__['__hash__']` to see the `None` Python placed there, and `Q(1).__hash__()` to see the number.
