## Hint 1

In `SingletonMeta.__call__(cls, *args, **kwargs)`, `cls` is the class being called
(`Settings`, or `TestSettings`). `super().__call__(*args, **kwargs)` does the normal
`__new__` + `__init__`. Where can you keep "the instance of *this exact* class" so that a
subclass does not see its parent's? (A dict keyed by the class? A check of `cls.__dict__`
rather than `hasattr`?)

For `InstanceCounter`: which metaclass method runs once for **every** class that is created,
subclasses included? That is where each class should get its own `instance_count = 0`.

## Hint 2

```
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]

class InstanceCounter(type):
    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace, **kwargs)
        cls.instance_count = 0
    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)     # may raise: then we never count
        cls.instance_count += 1
        return obj
```
