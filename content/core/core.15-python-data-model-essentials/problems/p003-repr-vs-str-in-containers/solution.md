## Approach

Follow the rule: top-level `print`, `str` and `f"{x}"` ask for `__str__`; everything inside a container, and `!r`, ask for `__repr__`. A class with only `__repr__` uses it for both.

## Output

```text
pen
Item('pen')
[Item('pen')]
(Item('pen'), 1)
{'k': Item('pen')}
pen / Item('pen')
[Item('pen')]
item: pen
<Plain>
[<Plain>] <Plain>
pen 'pen'
```

## Complexity

Not applicable.

## Another way

Add `print('str called')` / `print('repr called')` inside the methods and run the program; you will see exactly who calls which.
