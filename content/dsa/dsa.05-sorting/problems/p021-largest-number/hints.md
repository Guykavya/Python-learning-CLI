## Hint 1

For two numbers `3` and `30`, which of the strings `'330'` and `'303'` is larger? Does that decide who goes first?

## Hint 2

Define the order: `a` before `b` if `a + b > b + a` (string concatenation). It is a valid total order, so you can plug it into `sorted` through `functools.cmp_to_key`, returning `-1` when `a + b > b + a`.

## Hint 3

```
from functools import cmp_to_key
def cmp(a, b):
    if a + b > b + a: return -1
    if a + b < b + a: return 1
    return 0
parts = sorted(strings, key=cmp_to_key(cmp))
result = ''.join(parts); print('0' if result[0] == '0' else result)
```
