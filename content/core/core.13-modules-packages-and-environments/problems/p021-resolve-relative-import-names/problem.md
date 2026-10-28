# Resolve relative import names by hand

When Python sees `from ..core import db` inside the module `shop.api.views`, it turns the relative
name `..core` into the absolute name `shop.core` before it imports anything. The rule uses the
module's **package** (`__package__`):

- For a normal module, the package is the module name without its last part:
  `shop.api.views` -> `shop.api`.
- For a package's `__init__.py`, the module **is** the package: `shop.api` -> `shop.api`.
- One dot means "this package". Each extra dot goes **one level up**.
- The text after the dots is added at the end.

Write two functions in `solution.py`. Do **not** use `importlib.util.resolve_name`: the point is to
build the rule yourself (the tests check that the name does not appear in your file, and use it to
check your answers).

### `resolve_relative(name, module, is_package=False)`

Return the absolute module name.

- A name without a leading dot is already absolute: return it unchanged.
- If the package is empty (a top-level module like `main`, or a script), raise
  `ImportError("attempted relative import with no known parent package")`.
- If the dots go above the top-level package, raise
  `ImportError("attempted relative import beyond top-level package")`.

### `relative_name(target, module, is_package=False)`

The opposite direction: return the **shortest** relative name that `module` can use to import the
absolute module `target`. Raise `ValueError` if that is impossible (no package, or `target` is not in
the same top-level package).

So that both functions agree:
`resolve_relative(relative_name(t, m, p), m, p) == t` for every valid case.

## Example

```python
>>> resolve_relative(".utils", "shop.api.views")
'shop.api.utils'
>>> resolve_relative("..core.db", "shop.api.views")
'shop.core.db'
>>> resolve_relative(".", "shop.api.views")
'shop.api'
>>> resolve_relative(".views", "shop.api", is_package=True)
'shop.api.views'
>>> resolve_relative("...x", "shop.api.views")
Traceback (most recent call last):
ImportError: attempted relative import beyond top-level package
>>> resolve_relative(".helpers", "main")
Traceback (most recent call last):
ImportError: attempted relative import with no known parent package
>>> relative_name("shop.core.db", "shop.api.views")
'..core.db'
>>> relative_name("shop.api", "shop.api.views")
'.'
```
