## Hint 1

What does `reduce` do with an empty list if you give it no initial value?

## Hint 2

```
from functools import reduce

def product(numbers):
    return reduce(lambda acc, n: acc * n, numbers, 1)
```
