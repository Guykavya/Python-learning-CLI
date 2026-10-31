## Hint 1

`@singledispatch` turns the base function into a dispatcher. It looks at the type of the **first**
argument and picks the most specific registered version. How do you add a version for one type?

## Hint 2

Two ways to register: `@describe.register(int)` above a function, or `@describe.register` above a function
whose first parameter has a type hint (`def _(x: int):`). The name `_` is fine; you only call `describe`.

## Hint 3

```
@singledispatch
def describe(x): return f"unknown: {x!r}"

@describe.register
def _(x: int): ...even or odd...

@describe.register
def _(x: bool): return f"bool {x}"

@describe.register
def _(x: list):
    return f"list of {len(x)}: [" + ", ".join(describe(i) for i in x) + "]"
```
