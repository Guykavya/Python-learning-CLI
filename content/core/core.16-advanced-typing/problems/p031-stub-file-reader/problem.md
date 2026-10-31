# Read a stub file with ast

A **stub file** (`.pyi`) holds only the type information of a module: signatures with `...` as the
body. Type checkers read stubs for libraries that ship no hints of their own. A stub is ordinary
Python syntax, so the `ast` module can read it **without importing anything**. You will write a
tiny stub reader.

The folder `fixtures/` next to the tests has `geometry.pyi` (read it first). In `solution.py`
write four functions. Each takes `path` (a `str` or a `Path`) and parses the file with
`ast.parse(Path(path).read_text())`:

1. `stub_variables(path) -> dict[str, str]`
   Module-level annotated names, mapped to their annotation as text:
   `{"PI": "Final[float]", "VERSION": "str", ...}`. Use `ast.unparse(node.annotation)`.
   (Class attributes are not included.)
2. `stub_functions(path) -> dict[str, list[str]]`
   Every module-level function and every method of a module-level class, keyed by name
   (`"area"`, or `"Shape.area"` for a method). The value is a **list** of signature strings,
   because an overloaded function appears several times (in file order). A signature string is
   `"(" + ast.unparse(node.args) + ")"`, followed by `" -> " + ast.unparse(node.returns)` when there
   is a return annotation. An `async def` gets the prefix `"async "`.
   Example: `"area": ["(width: float, height: float) -> float"]`, `"Shape.area": ["(self) -> float"]`.
3. `stub_untyped(path) -> list[str]`
   The qualified names (as above, in file order) of functions or methods that are **not fully
   annotated**: a parameter without an annotation, or no return annotation. In a method, the first
   parameter (`self` or `cls`) needs no annotation.
4. `stub_classes(path) -> dict[str, list[str]]`
   Module-level class names mapped to the list of their base classes as text (`"Circle": ["Shape"]`,
   `"Shape": []`).

`ast.unparse(node.args)` turns the whole parameter list (defaults, `*`, `/`, `*args`) back
into text, so you do not have to rebuild it yourself. Use its output as it is: it writes an
annotated default as `shape: str=...` (no spaces around the `=`).

**Example** (from `geometry.pyi`)

```python
stub_variables(path)["PI"]          # "Final[float]"
stub_functions(path)["scale"]       # ["(factor: float, *, shape: str=...) -> float"]
stub_functions(path)["parse"]       # ["(text: str) -> int", "(text: str, as_float: bool) -> float"]
stub_untyped(path)                  # ["legacy", "Shape.helper"]
stub_classes(path)                  # {"Shape": [], "Circle": ["Shape"]}
```

**Remember**: the stub is data, not code to run. Never `import` or `exec` it. Only walk the tree.
Use `tree.body` to see module-level statements and `class_node.body` for the methods.
