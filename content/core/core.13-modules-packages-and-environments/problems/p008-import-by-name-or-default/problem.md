# Import a module by name, with a default

Programs often have **optional** dependencies: "use the fast library if it is installed, otherwise fall
back". The module name is often a string, for example from a settings file.

Write `import_or_default(name, default=None)` in `solution.py`.

- Import the module whose dotted name is the string `name` (for example `"json"` or `"os.path"`) with
  `importlib.import_module`, and return the module object.
- If that module **does not exist**, return `default`.
- Be careful: a module can exist but fail **inside** because it imports something else that is missing.
  That is a real bug in the module, and hiding it would make it very hard to find. So:
  `ModuleNotFoundError` has an attribute `.name`, the module that was not found. Return `default` only
  when `.name` is `name` itself, or one of its parents (for `"a.b.c"` the parents are `"a"` and `"a.b"`).
  Otherwise raise the error again.
- Any other error raised while the module runs (for example `ValueError`) must also go up unchanged.

**Example**

```python
import_or_default("json")                    # <module 'json' ...>
import_or_default("os.path").join("a", "b")  # 'a/b' on Linux and macOS
import_or_default("no_such_lib", "plain")    # 'plain'
import_or_default("no_such_lib.sub")         # None   ("no_such_lib" is a parent)

# broken.py exists and contains:  import not_installed_dependency
import_or_default("broken")                  # raises ModuleNotFoundError: No module named 'not_installed_dependency'
```
