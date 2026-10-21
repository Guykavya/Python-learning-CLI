## Hint 1

Where does `/` go in the parameter list, and what does it do to the parameters before it?

## Hint 2

```
def power(base, exp, /, *, modulo=None):
    if modulo is None:
        return base ** exp
    return pow(base, exp, modulo)
```
