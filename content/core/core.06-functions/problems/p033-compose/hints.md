## Hint 1

What does `compose` return: a value, or a function? Where is that function defined?

## Hint 2

Inside, define `def composed(x):` that loops over the functions in reverse order and applies each to a running value.

## Hint 3

```
def compose(*funcs):
    def composed(x):
        for f in reversed(funcs):
            x = f(x)
        return x
    return composed
```
