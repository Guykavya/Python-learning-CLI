# Your own lazy attribute

Some attributes are expensive to compute (parse a file, scan a big list) and many objects
never need them. A **lazy attribute** is computed the first time someone reads it and then
remembered. `functools.cached_property` does exactly this. Here you build your own, called
`lazy`, so you see the trick it relies on.

The trick: `lazy` is a **non-data descriptor** (it has `__get__` but no `__set__` and no
`__delete__`). On the first read, `obj.area` finds nothing in `obj.__dict__`, so Python calls
`lazy.__get__`. That method computes the value and **writes it into `obj.__dict__` under the
attribute's name**. On every later read the instance dictionary wins over the non-data
descriptor, so `__get__` is never called again.

Copy `starter.py` to `solution.py` and finish the class `lazy`:

- `lazy(func)` stores the function. Used as a decorator, `@lazy` above `def area(self): ...`.
- `__set_name__(self, owner, name)` remembers the attribute name. Use **this** name for the
  cache key, not `func.__name__`: in `total = lazy(_compute_total)` the cache key is `"total"`.
- `__get__(self, instance, owner=None)`:
  - when `instance is None` (read on the class, `Circle.area`), return the descriptor itself;
  - otherwise call `func(instance)`, store the result in `instance.__dict__[name]`, return it.
- Keep the function's docstring: `Circle.area.__doc__` is the docstring of `area`.
  Keep the function itself as the attribute `func`.
- Do **not** define `__set__` or `__delete__`. Because of that, `obj.area = 99` simply puts
  `99` in the instance dictionary, and `del obj.area` removes the cached value so the next read
  computes it again.

Results are cached even when they are `None`. If `func` raises, nothing is cached, so the next
read tries again.

**Example**

```python
class Circle:
    def __init__(self, r):
        self.r = r

    @lazy
    def area(self):
        """Area of the circle (pi taken as 3)."""
        print("computing...")
        return 3 * self.r * self.r

c = Circle(2)
vars(c)          # {'r': 2}            nothing computed yet
c.area           # prints computing... and gives 12
c.area           # 12, no print: it now comes from c.__dict__
vars(c)          # {'r': 2, 'area': 12}
del c.area       # forget the cached value
c.r = 3
c.area           # prints computing... and gives 27
Circle.area      # <solution.lazy object at 0x...>   (the address differs on your machine)
```
