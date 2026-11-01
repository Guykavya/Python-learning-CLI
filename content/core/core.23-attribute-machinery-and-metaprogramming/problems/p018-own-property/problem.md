# Build your own property

`property` is not magic syntax. It is an ordinary class written in C, and it is a **data
descriptor**. Writing it yourself in Python shows exactly what `@x.setter` does and why a
property without a setter refuses assignment.

Copy `starter.py` to `solution.py` and write the class `Prop` so that it behaves like
`property` for these uses (do not use `property` itself anywhere):

1. `Prop(fget=None, fset=None, fdel=None, doc=None)` stores the three functions as the
   attributes `fget`, `fset`, `fdel`. `__doc__` is `doc`, or, when `doc` is `None`, the
   docstring of `fget`.
2. `__get__`: on the class, return the `Prop` itself. On an instance, return `fget(instance)`.
   No getter: raise `AttributeError`.
3. `__set__(instance, value)` calls `fset(instance, value)`. **No setter: raise
   `AttributeError`**, and do not store anything. (Because `Prop` always defines `__set__`, it
   is always a data descriptor, so `c.area = 1` can never sneak into the instance dict.)
4. `__delete__(instance)` calls `fdel(instance)`; no deleter: `AttributeError`.
5. Every `AttributeError` message names the attribute, for example
   `property 'area' of 'Circle' object has no setter`. Get the name with `__set_name__`.
6. `getter(f)`, `setter(f)` and `deleter(f)` return a **new** object of the same class with
   that one function replaced and the rest (other functions, doc) copied. The original is
   **not changed**. That is what makes this pattern work:

   ```python
   @Prop
   def radius(self): ...          # radius = Prop(f1)
   @radius.setter
   def radius(self, value): ...   # radius = <that Prop>.setter(f2): a NEW Prop with f1 and f2
   ```

   and it lets a subclass add a setter (`@Base.value.setter`) without changing `Base`.
   "Same class" means `type(self)(...)`, so a subclass of `Prop` keeps its type.

**Example**

```python
class Circle:
    def __init__(self, r):
        self._r = r

    @Prop
    def radius(self):
        """The radius in cm."""
        return self._r

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("radius must be >= 0")
        self._r = value

    @Prop
    def area(self):
        return 3 * self._r ** 2

c = Circle(2)
c.radius               # 2
c.radius = 5           # runs the setter
c.area                 # 75
c.area = 1             # AttributeError: property 'area' of 'Circle' object has no setter
Circle.radius.__doc__  # 'The radius in cm.'
```
