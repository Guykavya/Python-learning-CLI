## Hint 1

In a definition, `*args` collects into a tuple and `**kw` into a dict. In a call, `*` and `**` spread.

## Hint 2

`show(nums)` passes ONE argument (a list). `show(*nums)` passes three. `*"ok"` passes two one-character strings.

## Hint 3

`pair(**{"b": 1, "a": 2})` is `pair(b=1, a=2)`, so `a` is 2 and `b` is 1, whatever order the dict has.
