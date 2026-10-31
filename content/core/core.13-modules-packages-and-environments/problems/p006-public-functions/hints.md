## Hint 1

`dir(shapes)` gives the names as strings. How do you get the **value** behind a name string?
(`getattr(module, name)`.) Then check the three rules one by one.

## Hint 2

```
result = []
for name in dir(module):
    if name starts with "_": skip
    value = getattr(module, name)
    if callable(value) and getattr(value, "__module__", None) == module.__name__:
        add name
return sorted(result)
```
