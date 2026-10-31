- Returning `vars(self)` itself. The caller then holds the real attribute dict and can change the object.
- Writing `to_dict` in `Student` and again in `Product`. The point of the mixin is to write it once.
- Giving the mixin an `__init__`. It would have to know every class's arguments, and it could stop the
  real class's `__init__` from running.
- Checking `name[0] == "_"` on the value instead of the key, or using `"_" in name` (that also drops
  `first_name`).
- Hard-coding the keys (`{"name": self.name, ...}`). Then the mixin only fits one class.
