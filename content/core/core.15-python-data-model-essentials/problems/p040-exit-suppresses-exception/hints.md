## Hint 1

When the block raises, Python calls `__exit__` with the exception class in `exc_type`. When it does not, `exc_type` is `None`. How can you test "is it one of my types or a subclass of one" in one expression? Which built-in takes a tuple of classes?

## Hint 2

`issubclass(exc_type, self.exc_types)` accepts a tuple. In `Expect`, the case `exc_type is None` is the **failure** case: `raise AssertionError(...)` from inside `__exit__` is allowed.

## Hint 3

```
Ignore.__enter__: exception = None ; return self
Ignore.__exit__: if exc_type is not None and issubclass(exc_type, types): exception = exc ; return True
                 return False
Expect.__exit__: if exc_type is None: raise AssertionError(f"expected {name}, ...")
                 if issubclass(exc_type, expected): store ; return True
                 return False
```
