## Approach

A relative name is "start at my package, go up `dots - 1` levels, then append the rest". Work on the
list of parts of the package name instead of on characters, so that `api` and `apiary` are never
confused. The opposite direction finds how many leading parts the target shares with the package:
the parts that are not shared must be climbed out of (one dot each, plus the dot for "this package"),
and the target's remaining parts are appended.

## Code

```python
def _package_of(module, is_package):
    return module if is_package else module.rpartition(".")[0]


def resolve_relative(name, module, is_package=False):
    if not name.startswith("."):
        return name
    package = _package_of(module, is_package)
    if not package:
        raise ImportError("attempted relative import with no known parent package")
    level = len(name) - len(name.lstrip("."))
    rest = name[level:]
    parts = package.split(".")
    if level > len(parts):
        raise ImportError("attempted relative import beyond top-level package")
    base = ".".join(parts[:len(parts) - (level - 1)])
    return f"{base}.{rest}" if rest else base


def relative_name(target, module, is_package=False):
    package = _package_of(module, is_package)
    if not package:
        raise ValueError(f"{module!r} has no package, so it cannot use relative imports")
    pkg_parts = package.split(".")
    target_parts = target.split(".")
    common = 0
    while (common < len(pkg_parts) and common < len(target_parts)
           and pkg_parts[common] == target_parts[common]):
        common += 1
    if common == 0:
        raise ValueError(f"{target!r} is not inside the top-level package of {module!r}")
    up = len(pkg_parts) - common
    return "." * (up + 1) + ".".join(target_parts[common:])
```

## Complexity

O(L) for names of length L.

## Another way

`package.rsplit(".", level - 1)` splits off exactly the parts you climb out of; if it gives fewer than
`level` pieces you went too high, otherwise the first piece is the base. This is how CPython's
`importlib._bootstrap._resolve_name` does it.

Now you can read the error from p022 with new eyes: running `python app/main.py` gives the module the
name `__main__` with no package, so step (1) gives an empty string and step (2) has nothing to start from.
