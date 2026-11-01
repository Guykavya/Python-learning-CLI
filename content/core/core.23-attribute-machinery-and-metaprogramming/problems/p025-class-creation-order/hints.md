## Hint 1

Split the program into three events: (1) the class `Base` is created, (2) the class `Point`
is created, (3) the instance `Point(1, 2)` is created. For each one ask: *which object is being
called right now?* A class statement calls the metaclass; making an instance calls the class,
which means calling the metaclass's `__call__`.

For `Base`, ask: is there a parent whose `__init_subclass__` prints? (`Base.__init_subclass__`
runs for subclasses of `Base`, not for `Base` itself.) Does `Base` contain any `Field`?

## Hint 2

The steps of a class statement, in order:

```
evaluate the decorator expression (deco)         # nothing printed
metaclass.__prepare__(name, bases, **kw)          -> empty namespace
run the class body inside that namespace          -> prints of the body, Field(...) calls
metaclass.__new__(mcls, name, bases, ns, **kw)
    ... super().__new__ = type.__new__:
            for each attribute with __set_name__: call it (definition order)
            parent.__init_subclass__(**kw)
    ... back in metaclass.__new__
metaclass.__init__(cls, name, bases, ns, **kw)
call the decorator: deco(cls)
```

And for `Point(1, 2)`: `Meta.__call__` → (inside `super().__call__`) `Point.__new__` →
`Point.__init__` → back in `Meta.__call__`.

The list `own` keeps only names that do **not** start with `__`, in the order the body defined them.
