# Write a helper module and import it

A module is just a `.py` file. Python can import it when its folder is on `sys.path`.

Write `create_module(folder, name, source)` in `solution.py`. `folder` is a `str` or a `Path`.

1. Write `source` into the file `<folder>/<name>.py` (UTF-8).
2. Put `str(folder)` at the **front** of `sys.path`, but only if it is not in `sys.path` already.
3. Call `importlib.invalidate_caches()`. Python remembers which files a folder had; this makes it look again.
4. Import the module by its name and return the **module object**.
5. If a module with this name was imported before (it is in `sys.modules`), the old code is still
   cached. In that case use `importlib.reload` so the **new** source runs.

**Example**

```python
mod = create_module("/tmp/demo", "greet", 'def hello(name):\n    return f"Hello, {name}!"\n')
print(mod.__name__)        # greet
print(mod.hello("Kavya"))  # Hello, Kavya!

mod = create_module("/tmp/demo", "greet", 'def hello(name):\n    return "Hi " + name\n')
print(mod.hello("Kavya"))  # Hi Kavya   (the new code, not the cached one)
```
