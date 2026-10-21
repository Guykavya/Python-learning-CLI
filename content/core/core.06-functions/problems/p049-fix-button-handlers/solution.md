## Approach

The loop has one variable that every closure shares, and the closures read it only when called.
A **factory function** fixes this: each call creates a new scope with its own variable, captured
by the function it returns. Because the factory's inner function takes exactly the parameters the
caller expects, the signatures stay clean.

## Code

```python
def make_click(name):
    """Return a handler that remembers this name in its own scope."""
    def handler():
        return "Clicked " + name
    return handler


def make_handlers(names):
    """Return {name: handler}; each handler takes no arguments and returns 'Clicked <name>'."""
    handlers = {}
    for name in names:
        handlers[name] = make_click(name)
    return handlers


def make_adder(i):
    """Return a function that adds i."""
    return lambda x: x + i


def make_adders(n):
    """Return [f0, f1, ...]; f_i(x) returns x + i."""
    return [make_adder(i) for i in range(n)]
```

## Complexity

O(n) to build n handlers; O(1) per call.

## Another way

`functools.partial` (from the standard library) can bind a value without a closure:
`partial(lambda name: "Clicked " + name, name)` returns a callable with no remaining parameters.
The default-argument trick (`lambda i=i: ...`) fixes the value too, but it changes the signature,
which this problem forbids for the handlers.
