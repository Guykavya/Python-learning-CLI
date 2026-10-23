See the model answer shown when you check. The ideas that must appear:

1. `apply_discount` has no hints, so by default mypy does not check its body, and treats its parameters and result as `Any`; a call with a `str` is accepted.
2. `--disallow-untyped-defs` (or `--strict`) reports every unannotated function. Adding `price: float, percent: float` and `-> float` lets mypy flag the call with `"100"`.
3. `average([])` has correct types: the argument is a `list[float]`. The crash (`ZeroDivisionError`) depends on the **value**, which types do not describe. Tests (core.08) and error handling (core.07) catch it.
4. `Any` and `# type: ignore` switch checks off locally. Each is a hole where wrong types can slip through unseen.
