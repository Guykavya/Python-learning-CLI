See the model answer shown when you check. The ideas that must appear:

1. `basicConfig` in a library takes over the root logger: everything becomes DEBUG, the format is imposed, and the app's own `basicConfig` is then ignored (the root already has a handler). `"my_logger"` is outside the package tree; use `__name__`. f-strings format eagerly; use `%` arguments. `log.exception` in an `except` block adds the traceback. `print` cannot be filtered or silenced.
2. Libraries: `getLogger(__name__)`, emit only, never configure handlers/levels/root; optional `NullHandler` on the package's top logger so nothing reaches `lastResort`.
3. Applications: configure once at the entry point (`basicConfig` / `dictConfig`); `basicConfig(level=WARNING)` plus `getLogger("pricing").setLevel(DEBUG)`.
4. Dotted names form a tree; a level on `pricing` is the effective level of all its children; records propagate to the root's handler.
