See the model answer shown when you check. The ideas that must appear:

1. `double_a(5)` is `int`, `double_a("ab")` is `str`: the TypeVar ties output to input. `double_u` always returns `int | str`, so the exact type is lost and follow-up code (`+ 1`) is rejected.
2. Constraints: `MyInt` matches the `int` constraint, `A = int`. Bound: `B = MyInt`, the subclass is kept.
3. A constrained TypeVar is checked once per constraint (`int`, then `str`), so `x + x` passes. A bound / union is checked once with "int or str" for each `x`, and `int + str` is possible: error.
4. Bound: "any subclass of X, keep the subtype". Constraints: closed list of unrelated types, same-in/same-out (`AnyStr`). Union: the output does not depend on the input type.
