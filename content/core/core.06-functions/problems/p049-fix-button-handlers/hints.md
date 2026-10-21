## Hint 1

When does each lambda look up `name`: when it is created, or when it is called? What is `name` by then?

## Hint 2

A factory function gives every handler its own scope. The adders need a two-level closure: a function that takes `i` and returns `lambda x: x + i`.

## Hint 3

```
def make_click(name):
    return lambda: "Clicked " + name

def make_handlers(names):
    return {name: make_click(name) for name in names}

def make_adder(i):
    return lambda x: x + i
```
