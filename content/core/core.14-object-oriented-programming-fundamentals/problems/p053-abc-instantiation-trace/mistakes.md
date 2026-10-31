- Thinking `Square(2)` works because it has an `__init__` and `area`. One abstract method left
  (`name`) is enough to block it.
- Thinking `NamedSquare` fails because `area` was overridden in a *different* class. Any class in the
  chain may override it.
- Writing `triangle has area None` or an error for `super().area()`. An abstract method can have a
  normal body, here `return 0`.
- Writing `True` for `isinstance(Blob(), Shape)` before `register`. ABCs do not compare method names
  unless the ABC is written to do that (some in `collections.abc` are).
- Thinking `register` adds `Shape` to the MRO or gives `Blob` the `describe` method. It only changes
  what `isinstance` and `issubclass` answer.
- Writing a `TypeError` for `Shape.area(sq)`. Only **creating** an instance of an abstract class is
  blocked; calling its methods is fine.
