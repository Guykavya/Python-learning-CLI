- Writing `x = x` in `__init__` instead of `self.x = x`. That only makes a local variable that
  disappears when `__init__` ends; the object gets no attribute.
- Forgetting `self` as the first parameter. `def distance_to(other):` makes `a.distance_to(b)` fail
  with "takes 1 positional argument but 2 were given", because Python passes `a` too.
- Changing the point in `moved`: `self.x += dx; return self`. The caller's original point moves too.
- Returning a tuple `(x, y)` from `moved`. The caller can then no longer call `.distance_to()` on it.
- Writing `sqrt(dx + dy)` without squaring. A negative difference would then cancel a positive one.
