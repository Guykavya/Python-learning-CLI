## Hint 1

Do it in three steps. (1) What is the package of `module`? (Think of `rpartition(".")` and the
`is_package` flag.) (2) How many dots does the name start with, and what text is left after them?
(3) Split the package into parts: with `k` dots, how many parts do you keep?

## Hint 2

```text
resolve_relative:
    if name has no leading dot: return name
    package = module if is_package else module.rpartition(".")[0]
    if package == "": raise ImportError(... no known parent package)
    level = number of leading dots;  rest = name[level:]
    parts = package.split(".")
    if level > len(parts): raise ImportError(... beyond top-level package)
    base = ".".join(parts[: len(parts) - (level - 1)])
    return base + "." + rest  if rest else base

relative_name:
    pkg_parts, target_parts; count common leading parts (whole parts, not characters)
    common == 0 -> ValueError
    up = len(pkg_parts) - common
    return "." * (up + 1) + ".".join(target_parts[common:])
```
