## Hint 1

You need three steps per file: find it, load it, look inside it. Which `Path` method lists only the
`.py` files directly in a folder? How do you load a file when you only know its path, and why is
`importlib.import_module` a bad fit here (think of `sys.path` and the module cache)?

## Hint 2

```text
folder = Path(folder); if not a dir -> raise FileNotFoundError
for path in sorted(folder.glob("*.py")):
    skip if path.name starts with "_"
    try:
        spec = spec_from_file_location("plugin_" + stem, path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception:
        failed.append(stem); continue
    register = getattr(module, "register", None)
    if callable(register): plugins[stem] = register
return plugins, failed
```

`run_plugins` loops over the dict and calls each function with `app`.
