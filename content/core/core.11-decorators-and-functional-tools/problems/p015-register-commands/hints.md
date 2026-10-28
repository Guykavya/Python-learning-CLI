## Hint 1

`@register(COMMANDS, "add")` calls `register` first, so `register` must return a decorator. What does that
decorator do with `func`, and what must it return so that `add` is still a function afterwards?

## Hint 2

In `run_command`, `line.split()` gives `["add", "2", "3"]`. How do you call a function with a list of values
as separate arguments?

## Hint 3

```
register(registry, name):
    def decorate(func):
        if name in registry: raise ValueError(...)
        registry[name] = func
        return func
    return decorate

run_command(registry, line):
    parts = line.split()
    if not parts: raise ValueError("empty command")
    name = parts[0]
    if name not in registry: raise ValueError(...)
    return registry[name](*[int(w) for w in parts[1:]])
```
