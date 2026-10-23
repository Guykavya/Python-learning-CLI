**1. Why `apply_discount("100", 10)` passes.** By default mypy is lenient: a function with **no
hints at all** is not checked. Its body is skipped, and its parameters and result are treated as
`Any`, so a call with a string is accepted. "mypy passes" only means something where hints exist.

**2. Making mypy insist.** `--disallow-untyped-defs`, or `--strict`, reports every function
without hints. To make mypy catch the call, Nisha must write
`def apply_discount(price: float, percent: float) -> float:`. Then `"100"` is an `[arg-type]`
error.

**3. Why `average([])` passes.** Its types are right: `[]` is a `list[float]`. The crash,
`ZeroDivisionError`, comes from the **value** (the list is empty), and types do not describe
values. That is a job for tests (core.08), which would include the empty list, and for error
handling (core.07), such as checking `if not prices` first.

**4. Switching checks off.** The type `Any` and the comment `# type: ignore` both tell mypy to
stop looking at a spot. They are risky because every one is a hole where a wrong type can pass
unnoticed. Use them rarely, prefer `# type: ignore[code]`, and explain why.
