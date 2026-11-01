## Hint 1

Inside `__init_subclass__`, `cls` is the **new** subclass, not `Plugin`. If you wrote
`cls.registry[key] = cls`, which dict would that change? (Is `registry` copied to subclasses or
found on `Plugin` through inheritance?) What should happen to keywords that `Plugin` does not
understand?

## Hint 2

```
__init_subclass__(cls, /, key=None, **kwargs):
    super().__init_subclass__(**kwargs)
    if key is None: return
    if key in Plugin.registry: raise ValueError(mention key)
    cls.key = key
    Plugin.registry[key] = cls

create(cls, key, *args, **kwargs):
    look up Plugin.registry[key]; turn a miss into KeyError with a helpful message
    return the_class(*args, **kwargs)
```
