## Hint 1

`partial(power, 2)` fixes the **first** positional argument. Which parameter is first in `power(base, exp)`?
Is that the one you want to fix?

## Hint 2

Fix the parameter by name, so the caller's value fills the other one.

```
square = partial(power, exp=2)
from_binary = partial(int, base=2)
```
