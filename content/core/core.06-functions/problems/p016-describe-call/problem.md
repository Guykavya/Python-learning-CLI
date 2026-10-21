# Describe a forwarded call

Write `describe_call(func, *args, **kwargs)` that calls `func` with exactly the arguments it was
given, and returns a string describing the call and its result:

```
<func name>(<arguments>) -> <repr of result>
```

- Positional arguments are shown with `repr`, in order.
- Keyword arguments follow, as `name=repr(value)`, in the order they were passed.
- Arguments are separated by `", "`.
- `func` must be called **exactly once**.

A function's name is in its `__name__` attribute.

**Examples**

```python
def add(a, b):
    return a + b

describe_call(add, 2, 3)                # "add(2, 3) -> 5"
describe_call(add, "a", b="b")          # "add('a', b='b') -> 'ab'"
describe_call(len, [1, 2])              # "len([1, 2]) -> 2"
describe_call(sorted, [3, 1], reverse=True)   # "sorted([3, 1], reverse=True) -> [3, 1]"
```
