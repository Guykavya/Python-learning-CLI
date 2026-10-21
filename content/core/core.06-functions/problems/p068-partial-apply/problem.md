# Pre-fill some arguments

Write `partial_apply(func, *args, **kwargs)` that returns a new function `g`. Calling
`g(*more_args, **more_kwargs)` calls `func` with:

- the stored positional arguments first, then `more_args`;
- the stored keyword arguments, updated with `more_kwargs` (a keyword given at call time
  **overrides** a stored one of the same name);

and returns its result. The stored arguments must not change between calls. Do not use
`functools.partial`; this is your own version of it.

**Examples**

```python
def describe(name, age, city="Pune", sep=", "):
    return f"{name}{sep}{age}{sep}{city}"

asha = partial_apply(describe, "Asha")
asha(19)                        # 'Asha, 19, Pune'
asha(20, city="Delhi")          # 'Asha, 20, Delhi'

dashed = partial_apply(describe, sep=" - ")
dashed("Ravi", 21)              # 'Ravi - 21 - Pune'
dashed("Ravi", 21, sep="/")     # 'Ravi/21/Pune'
dashed("Meena", 30)             # 'Meena - 30 - Pune'   (the override did not stick)

int_from_binary = partial_apply(int, base=2)
int_from_binary("1011")         # 11
```
