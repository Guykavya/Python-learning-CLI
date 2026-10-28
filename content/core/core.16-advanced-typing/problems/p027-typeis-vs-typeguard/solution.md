The ideas that must appear:

1. A `str`, B `int | str`, C `str`, D `int` (verified with mypy 2.4.0).
2. `TypeGuard` narrows only when True; `TypeIs` narrows both ways, because it promises True exactly when the value has that type. So `TypeIs` removes `str` from the union in the else branch.
3. A `TypeIs` function that returns False for some real members of the type (an empty `str`) makes a false promise, and the checker believes it. Use `TypeGuard`, which promises nothing in the False case.
4. `TypeIs` needs the narrowed type to be a subtype of the input type; `list[str]` is not a subtype of `list[object]` (invariance), so only `TypeGuard` is allowed. (mypy reports `[narrowed-type-not-subtype]`.)

Rule of thumb: if the function is a pure type test (like `isinstance`), use `TypeIs`. If it
checks extra conditions, or narrows to something that is not a subtype, use `TypeGuard`.
