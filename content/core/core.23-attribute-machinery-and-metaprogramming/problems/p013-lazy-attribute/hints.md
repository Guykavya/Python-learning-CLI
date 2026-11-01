## Hint 1

Remember the lookup order for `obj.area`: data descriptors on the class first, then the
instance `__dict__`, then non-data descriptors and plain class attributes. If `lazy` has only
`__get__`, which of these wins **after** you have put `"area"` into `obj.__dict__`? So what is
the only thing `__get__` has to do besides computing?

## Hint 2

```
__init__(func):     keep func; copy func.__doc__ onto self.__doc__
__set_name__(owner, name): self.name = name

__get__(instance, owner=None):
    if instance is None: return self          # read on the class
    value = self.func(instance)
    instance.__dict__[self.name] = value      # from now on the instance dict answers
    return value
```

No `__set__`, no `__delete__`: assignment and `del` then work on the instance dict for free.
