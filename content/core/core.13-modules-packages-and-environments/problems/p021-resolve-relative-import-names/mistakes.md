- Using the module name instead of its package: `.utils` from `shop.api.views` is `shop.api.utils`,
  not `shop.api.views.utils`.
- Cutting the last part off a package `__init__` too. With `is_package=True` the module is the package.
- Going up one level for **each** dot. The first dot means "here"; only the extra dots go up.
- Comparing names with `startswith` on strings: `"shop.apiary".startswith("shop.api")` is `True`
  but they share only `shop`. Compare lists of parts.
- Returning `"shop.api."` for the name `.`. When the rest is empty, there is no trailing dot.
