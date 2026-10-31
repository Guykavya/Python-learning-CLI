**1. The revealed types.** A: `str`. B: `int | str` (nothing is learned). C: `str`. D: `int`.

**2. Why B and D differ.** Both functions return exactly the same bool. The difference is only
the promise made to the checker. `TypeGuard[str]` says: "if I return True, the value is a `str`".
It says nothing when the result is False, so in the `else` branch the checker keeps `int | str`.
`TypeIs[str]` says more: "the result is True **exactly when** the value is a `str`". So when it is
False the value is *not* a `str`, and the checker removes `str` from the union, leaving `int`.
`TypeIs` therefore behaves like `isinstance`; `TypeGuard` only narrows the positive branch.

**3. The non-empty check.** With `TypeIs[str]`, a False result would mean "this is not a str". But
`is_non_empty("")` returns False for a value that **is** a str. The checker would wrongly treat `""`
as not-a-str in the `else` branch (it would think it is an `int`). The promise is false, and the
checker trusts it. She should use `TypeGuard[str]`: the function only claims something about the
True case (a non-empty str is a str), and says nothing about False.

**4. Only `TypeGuard`.** `TypeIs` requires the narrowed type to be a subtype of the input type.
`list[str]` is not a subtype of `list[object]` (lists are invariant), so
`def all_str(x: list[object]) -> TypeIs[list[str]]` is rejected and you must write `TypeGuard`.
The same goes for any check that narrows to a type that is not a subtype, or that is a
"validated" check rather than a pure type test.
