The ideas that must appear:

1. Add an empty `py.typed` file inside the package (and include it in the distribution). It tells checkers that the package ships usable hints (PEP 561). Without it the installed package is treated as untyped.
2. Options for an untyped third-party library: install a stub package (`types-xxx`, a separate package of `.pyi` files, from typeshed), write a local `.pyi` stub, or silence the import. A `types-requests` package gives type information for `requests` without changing it. Silencing makes the library's contents `Any`, so nothing is checked and `Any` spreads.
3. Annotate the source when you own it. Write a stub when you cannot edit the code (third party, C extension), or to describe only the part you use.
4. Migrate gradually: start lenient, annotate boundaries first, enable strict per module, block regressions in CI, keep `Any`/ignores visible.
