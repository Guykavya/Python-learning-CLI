## Approach

A module is an object, and its global names are its attributes. `dir(module)` gives the names;
`getattr(module, name)` gives each value. Three checks decide if a name is part of the module's own public
API: no leading underscore, callable, and `__module__` equal to the module's own `__name__`. Imported
functions keep the `__module__` of the module that defined them, so this check drops them.

## Code

```python
def public_functions(module):
    result = []
    for name in dir(module):
        if name.startswith("_"):
            continue
        value = getattr(module, name)
        if callable(value) and getattr(value, "__module__", None) == module.__name__:
            result.append(name)
    return sorted(result)
```

## Complexity

O(n log n) for n names in the module (the sort). `dir` already returns a sorted list, so sorting again
is cheap, but it states the promise clearly.

## Another way

`vars(module)` (or `module.__dict__`) is the module's namespace as a dictionary, so you can loop over
`vars(module).items()` and get the name and value together. A comprehension makes it one line:

```python
return sorted(n for n, v in vars(module).items()
              if not n.startswith("_") and callable(v) and getattr(v, "__module__", None) == module.__name__)
```
