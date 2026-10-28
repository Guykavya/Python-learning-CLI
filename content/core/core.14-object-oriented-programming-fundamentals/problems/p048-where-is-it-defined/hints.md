## Hint 1

`hasattr(Child, "save")` is `True` even though `Child` does not define `save`: it looks through the
parents. Which check tells you whether **this one class** has the name in its own namespace? Try
`vars(Child)` and `vars(Left)` in the REPL and look at the keys.

## Hint 2

Why not walk `cls.__bases__` yourself? Write the MRO of `Child` from the example, and compare it
with a depth-first walk `Child, Left, Base, Right`. Python already gives you the right order in
`cls.__mro__`.

## Hint 3

```text
defined_in(cls, name):
    if cls is not a class: raise TypeError(...)
    for klass in cls.__mro__:
        if name in vars(klass): return klass
    return None

all_definitions(cls, name):
    same check
    return [klass.__name__ for each klass in cls.__mro__ if name in vars(klass)]
```
