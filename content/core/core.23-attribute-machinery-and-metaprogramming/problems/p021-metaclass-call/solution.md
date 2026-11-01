## Approach

Calling a class goes through its metaclass's `__call__`. Overriding it lets you wrap the
normal creation (`super().__call__`) with your own logic.

**Singleton**: keep a dictionary from class to its single instance. Looking up the exact
class object as a key cannot accidentally find a parent's instance, which is the trap with
`hasattr(cls, "_instance")` (attribute lookup on a class walks its MRO). Store only after
`super().__call__` returned, so a failed `__init__` stores nothing.

**Counter**: the metaclass `__init__` runs once per class created with it, including every
subclass, so it can give each class its own `instance_count = 0`. Then `cls.instance_count += 1`
reads and writes the class's own attribute. Without that per-class initialisation, the first
`ColorPoint()` would read `Point`'s count through inheritance and write `Point's count + 1`
onto `ColorPoint`.

## Code

```python
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
        obj = super().__call__(*args, **kwargs)
        cls.instance_count += 1
        return obj
```

## Complexity

O(1) extra work per instance creation in both metaclasses.

## Another way

Store the singleton in the class's **own** namespace and test it there, not through
inheritance:

```python
def __call__(cls, *args, **kwargs):
    if "_instance" not in cls.__dict__:
        cls._instance = super().__call__(*args, **kwargs)
    return cls._instance
```

For the counter, a dictionary on the metaclass and a `property` defined on the metaclass also
work: `Point.instance_count` then reads `InstanceCounter._counts[Point]`.

Before reaching for a metaclass singleton, remember the lighter Python options from core.22: a
module is already a singleton (import it), and a module-level instance (`settings = Settings()`)
is usually all you need. Metaclass `__call__` earns its place when instance creation itself
must be controlled for a whole family of classes, for example caching or registering every
instance.
