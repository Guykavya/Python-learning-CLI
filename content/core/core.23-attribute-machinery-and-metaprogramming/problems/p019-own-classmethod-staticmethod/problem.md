# Build your own classmethod and staticmethod

A plain function in a class becomes a bound method because functions are non-data
descriptors: `function.__get__(obj, cls)` returns a method with `__self__ = obj`.
`classmethod` and `staticmethod` are just **other descriptors** that bind differently:

| decorator | `__get__(instance, owner)` returns | first argument the function gets |
|---|---|---|
| none (plain function) | method bound to `instance` | the instance |
| `classmethod` | method bound to `owner` (the class) | the class, even when called on an instance |
| `staticmethod` | the plain function itself | nothing extra |

Copy `starter.py` to `solution.py` and write `ClassMethod` and `StaticMethod` (without using
the built-in `classmethod` or `staticmethod`):

**`ClassMethod(func)`**
- keeps the function as `__func__`;
- `__get__(instance, owner=None)` returns a real **bound method** whose `__self__` is the
  class: use `types.MethodType(func, cls)`. When `owner` is not given (someone calls
  `desc.__get__(obj)` directly), the class is `type(instance)`;
- so `Sub.create()` and `Sub().create()` both pass `Sub`, never the parent class.

**`StaticMethod(func)`**
- keeps the function as `__func__`;
- `__get__` returns the function itself, unchanged, for class and instance access;
- the `StaticMethod` object is itself callable (`__call__`), like the real `staticmethod`
  since Python 3.10, so code that grabs it from the class `__dict__` can still call it.

**Example**

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @ClassMethod
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)

    @StaticMethod
    def c_to_f(c):
        return c * 9 / 5 + 32

class Lab(Temperature):
    pass

Temperature.from_fahrenheit(212).celsius   # 100.0
type(Lab.from_fahrenheit(32))              # <class '__main__.Lab'>   the subclass, not Temperature
Lab(5).from_fahrenheit(212)                # also a Lab: cls is the class, not the instance
Temperature.c_to_f(100)                    # 212.0
Temperature(0).c_to_f(0)                   # 32.0, no self is passed
Temperature.from_fahrenheit.__self__       # <class '__main__.Temperature'>
```
