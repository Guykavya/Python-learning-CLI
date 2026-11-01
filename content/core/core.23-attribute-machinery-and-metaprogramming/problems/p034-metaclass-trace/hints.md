## Hint 1

Work out the metaclass of each class first, before tracing any print:

- `A`: given explicitly.
- `B`: given explicitly.
- `C(A, B)`: the candidates are `type(A)` and `type(B)`. Which one is a subclass of the other?
- `D(C)`: inherits from `C`.
- `E(A, metaclass=Other)`: is `Other` a subclass of `MetaA`, or `MetaA` a subclass of `Other`?

Then note: `MetaB` defines no `__new__`, so creating a class with `MetaB` still runs `MetaA.__new__`
(inherited), with `mcls` set to `MetaB`. And `A.__init_subclass__` runs for every class below `A`, never for `A`.

## Hint 2

```
class statement:
    pick the most derived metaclass  (conflict? -> TypeError, no prints at all)
    MetaX.__new__  -> prints "MetaA.__new__ mcls=... class=..."
        inside type.__new__: A.__init_subclass__(prefix=...)  (only if A is a base)

C(n), when type(C) is MetaB:
    print "MetaB.__call__ C(n,)"
    type.__call__:
        obj = C.__new__(C, n)          -> prints "C.__new__ n"
        if isinstance(obj, C): C.__init__(obj, n)
    print "got <type of obj>"
```

`D(2)` uses `C.__new__` and `C.__init__` (inherited), but `cls` is `D`.
