- `except ImportError: return default` or `except Exception`. It hides real bugs: a module that exists
  but imports something missing looks "not installed", and you search in the wrong place.
- Using `startswith(e.name)` without the dot. `"broken"` starts with `"bro"`, so a missing module `bro`
  would look like a parent.
- Using `__import__("os.path")`. It returns the top package `os`, not `os.path`. `import_module` returns
  the module you named.
- Calling `exec(f"import {name}")`. It works by accident and is unsafe with strings from outside.
