**1. Meera.** She must ship an empty marker file named `py.typed` inside the package directory
(`textkit/py.typed`) and make sure it is included in the built distribution (package data in
`pyproject.toml`). It is a promise from the author: "my hints are meant to be used". Without it,
type checkers assume an installed package is untyped and ignore its hints (PEP 561).

**2. Karan.** Options: (a) install a stub package if one exists (`pip install types-requests`):
these are separate packages with `.pyi` files that describe a library written by someone else (they
come from the typeshed project); (b) write a small local stub, `oldlib.pyi`, in a `stubs/` folder
and point mypy at it (`mypy_path`); (c) silence it with `ignore_missing_imports` or
`# type: ignore[import-untyped]`. With (c), the module's contents become `Any`, so nothing
about `oldlib` is checked and the `Any` spreads into any code that uses its results.

**3. Stub or source.** If I own the code, annotate the source: one place to maintain, and the
hints stay next to the code. I write a `.pyi` stub when I cannot edit the code (a third-party
library, a C extension, generated code), or when I only need to describe the part I use
(a partial stub is enough).

**4. Isha.** Go gradually. Start with a plain config (no `strict`), fix the errors that appear,
then turn strictness on per module: `[[tool.mypy.overrides]]` with `strict = true` for new and
fully typed modules, while old modules stay lenient (`disallow_untyped_defs = false`). Annotate
the public functions at the boundaries first, add checks in CI so the typed area never shrinks,
and track the number of `Any`/`# type: ignore` over time.
