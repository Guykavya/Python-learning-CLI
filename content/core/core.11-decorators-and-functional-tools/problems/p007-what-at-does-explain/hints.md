## Hint 1

Write the decoration without the `@` sign. What is assigned to which name? Is that line inside a function
call, or does it run when the `def` runs?

## Hint 2

Answer in order: (1) the assignment and its timing, (2) which object `total` is now, (3) `@wraps(func)` on
the wrapper and the attributes it copies (`__name__`, `__doc__`, `__qualname__`, `__module__`, `__wrapped__`),
(4) two real problems: `help()`, logs, registries, stacked decorators, test reports.
