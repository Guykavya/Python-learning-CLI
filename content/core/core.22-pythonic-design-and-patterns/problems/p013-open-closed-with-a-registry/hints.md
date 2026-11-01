## Hint 1

What do the three `elif` branches have in common, and what differs? If the "what differs" part
(the formula) were a function stored under the shape's name, what would `area` have to do? Where
does a decorator get the name it should store the function under (hint: a decorator with an
argument is a function that returns a decorator)?

## Hint 2

```
_AREAS = {}
def register(name):
    def decorator(func):
        refuse if name already in _AREAS (ValueError)
        _AREAS[name] = func
        return func
    return decorator

def shape_names(): return sorted(_AREAS)

@register("circle") def _circle(shape): ...   (and rect, square)

def area(shape):
    kind = shape["type"]
    try: func = _AREAS[kind]
    except KeyError: raise ValueError("unknown shape: " + kind) from None
    return func(shape)
```
