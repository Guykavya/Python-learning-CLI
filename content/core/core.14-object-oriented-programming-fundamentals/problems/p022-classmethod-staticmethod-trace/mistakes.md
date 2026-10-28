- Thinking a classmethod always gets the class where it was **written** (`Shape`). It gets the class it
  was **called on**.
- Thinking `t.describe()` passes the instance `t` as `cls`. Through an instance, `cls` is `type(t)`.
- Thinking `create` returns a `Shape`. It returns `cls(label)`, a `Square` or `Triangle`.
- Expecting separate `made` lists per subclass. `cls.made.append(...)` only reads `made`, which is
  found in `Shape`, so there is one list.
- Thinking `self.unit()` always gives `cm`. The lookup starts at the object's own class, `Square`.
- Thinking `Triangle.sides = 30` changes `Shape.sides` too. Assignment writes only to `Triangle`.
