**1. Inference and why a union is weaker.** For `double_a(5)` the checker solves `A = int`, so the
result is `int`; for `double_a("ab")` it solves `A = str` and the result is `str`. The TypeVar
**links** the argument type to the result type. `double_u(5)` is declared to return
`int | str`, whatever came in: the checker has forgotten that the result is an `int`, so
`double_u(5) + 1` is reported as an error (the `str` half of the union cannot take `+ 1`). A union
only describes what is allowed in; it cannot say "the output has the same type as the input".

**2. A subclass.** With constraints, the argument must match one of the listed types, and the
checker picks that constraint: `MyInt` is an `int`, so `A` is solved as exactly `int`, and the
result is `int` (the subclass is "forgotten", even though at runtime a `MyInt` goes in; for
`x + x` that is normal). With a bound, `B` is solved as the actual type of the argument:
`double_b(MyInt(3))` has `B = MyInt` and the result is a `MyInt`. A bound keeps subclasses;
constraints collapse to one of the listed types.

**3. Why only one version type-checks.** For a constrained TypeVar the checker checks the body
**once per constraint**, replacing `A` by `int`, then by `str`. `int + int` is fine, `str + str`
is fine, so the body passes. For a bound, the body is checked once with `B` as "some type that is
at most `int | str`"; the checker cannot know that both `x`s are the same half of the union, and
`x + x` could in principle be `int + str`: error. The plain union has the same problem, plus the
result is declared as the whole union.

**4. When to use which.**
- **Bound**: any subclass of a base class or protocol is fine, and the result should keep the
  exact subtype. Example: `def longest(items: Iterable[S]) -> S` with `S` bound to `Sized`.
- **Constraints**: a small, closed list of unrelated types, with the output type tied to the
  input type, and the body must work for each one. Example: `AnyStr` (`str` or `bytes`): a
  function must never mix the two.
- **Plain union**: the input may be one of several types but the output does **not** depend on which one it was, or the function
  just branches on `isinstance`. Example: `def show(x: int | str) -> str`.
