## Approach

`partial` stores a function and some arguments. Positional ones go first, in order. Keyword ones are
matched by name. Here we want to fix the **second** parameter of `power`, so a keyword is the right tool:
`partial(power, exp=2)`. A later call `square(5)` becomes `power(5, exp=2)`.
`int` has a `base` keyword, so `partial(int, base=2)` turns it into a binary parser.

## Code

```python
from functools import partial


def power(base, exp):
    return base ** exp


square = partial(power, exp=2)
cube = partial(power, exp=3)
from_binary = partial(int, base=2)
from_hex = partial(int, base=16)
```

## Complexity

O(1) to build. Each call costs one call of the underlying function.

## Another way

`def square(base): return power(base, 2)` or `lambda base: power(base, 2)` behave the same. `partial` is
shorter, shows its intent, and can be inspected (`.func`, `.args`, `.keywords`), which helps when you
debug or log it.
