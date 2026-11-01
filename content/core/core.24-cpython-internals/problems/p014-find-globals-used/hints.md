## Hint 1

Print `[(i.opname, i.argval) for i in dis.get_instructions(price)]` and find the instructions
that load `RATE`, `round` and `math`. Which opname do they share, and which opname loads `cost`?
Then print `report.__code__.co_consts`: where is the code of the inner function `line`?
For `undefined_globals`, which two dictionaries does Python search when `LOAD_GLOBAL` runs?

## Hint 2

```
loads(code):
    names = {ins.argval for ins in get_instructions(code) if ins.opname == "LOAD_GLOBAL"}
    for const in code.co_consts:
        if const is a code object:
            names |= loads(const)          # recursion handles any depth
    return names

globals_used(func)      = sorted(loads(func.__code__))
undefined_globals(func) = [n for n in globals_used(func)
                           if n not in func.__globals__ and n not in vars(builtins)]
```
