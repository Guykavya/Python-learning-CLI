# Controlling instance creation with a metaclass `__call__`

`Point(1, 2)` is a **call of the class object**. A class is an instance of its metaclass, so
the call runs `type(Point).__call__(Point, 1, 2)`. The default `type.__call__` does the two
steps you know: `obj = cls.__new__(cls, ...)` and then `obj.__init__(...)`. A metaclass that
overrides `__call__` sits in front of both and can decide what "calling the class" means.

Copy `starter.py` to `solution.py` and write two metaclasses.

**`SingletonMeta`**: every class that uses it has at most one instance.

- The first call creates the instance normally (`super().__call__(*args, **kwargs)`), and every
  later call returns that same object. `__init__` therefore runs only once; the arguments of
  later calls are ignored.
- **Each class has its own instance**, subclasses included. If `Settings` is a singleton and
  `TestSettings(Settings)` is created after `Settings`, then `TestSettings()` is a new
  `TestSettings`, not the `Settings` object. (A `hasattr(cls, "_instance")` check gets this
  wrong: it finds the parent's instance through inheritance.)
- If `__init__` raises, nothing is remembered, so the next call tries again.

**`InstanceCounter`**: every class that uses it gets a class attribute `instance_count`.

- It starts at `0` for each class, including each subclass.
- It goes up by one each time an instance is created **successfully** (not when `__init__` raises).
- Subclasses count separately: creating a `ColorPoint(Point)` raises `ColorPoint.instance_count`
  and leaves `Point.instance_count` as it was.

**Example**

```python
class Settings(metaclass=SingletonMeta):
    def __init__(self, debug=False):
        self.debug = debug

a = Settings(debug=True)
b = Settings()               # same object; __init__ not run again
a is b, b.debug              # (True, True)

class Point(metaclass=InstanceCounter):
    def __init__(self, x, y):
        self.x, self.y = x, y

class ColorPoint(Point):
    pass

Point(0, 0); Point(1, 1); ColorPoint(2, 2)
Point.instance_count, ColorPoint.instance_count     # (2, 1)
```
