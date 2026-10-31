- A decorator that forgets `return cls`. After `@register_shape class Circle`, the name `Circle` is
  `None`.
- Writing `from_args` in every subclass. One classmethod in `Shape` that reads `cls.n_args` is enough.
- Checking the numbers before the count. `rect abc` must report the count, as problem.md says.
- Counting only the non-skipped lines. Line numbers must match what the user sees in the file.
- Letting the `KeyError` escape from `parse_shape`. The caller should get an `UnknownShapeError` that
  says which kind was wrong.
- Catching `Exception` in `parse_shapes`. A bug in a shape's `__init__` (a `NameError`) would be turned
  into "bad line".
- In `parse_all`, raising at the first error, or putting plain `ValueError`s into the group instead of
  `BadShapeLine`s with line numbers.
