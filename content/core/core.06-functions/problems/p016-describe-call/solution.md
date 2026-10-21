## Approach

In the definition, `*args` and `**kwargs` collect the arguments; in the body,
`func(*args, **kwargs)` spreads them back out exactly as they came in. Call once and keep the
result. Then build the description from `repr` of each positional and `name=repr` of each keyword
(dicts keep insertion order), joined with `", "`. The `!r` in an f-string means "use repr".

## Code

```python
def describe_call(func, *args, **kwargs):
    """Call func(*args, **kwargs) once and return 'name(args) -> repr(result)'."""
    result = func(*args, **kwargs)
    parts = [repr(a) for a in args]
    parts += [f"{k}={v!r}" for k, v in kwargs.items()]
    return f"{func.__name__}({', '.join(parts)}) -> {result!r}"
```

## Complexity

O(size of the arguments) to build the text, plus whatever `func` costs.

## Another way

A loop that appends to `parts` instead of the comprehensions. This forwarding pattern is the
heart of decorators, which a later module covers: a wrapper that takes `*args, **kwargs` and
passes them on untouched works for any function.
