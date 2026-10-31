## Hint 1

Which list does `import` search for files? If you add the folder at position 0, what happens when two
calls use the same folder? Check with `in` before you insert.

## Hint 2

`importlib.import_module("greet")` does the same work as `import greet`, but the name is a string.
What does it return when `"greet"` is already a key in `sys.modules`?

## Hint 3

```
path = Path(folder)
write source to path / (name + ".py") with encoding="utf-8"
if str(path) not in sys.path: sys.path.insert(0, str(path))
importlib.invalidate_caches()
if name in sys.modules: return importlib.reload(sys.modules[name])
return importlib.import_module(name)
```
