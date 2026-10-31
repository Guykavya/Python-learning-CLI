## Approach

A decorator does not have to wrap. This one just records the function as a side effect and returns it
as it is. Because decoration happens at definition time, the table is full as soon as the module is
imported. `run_command` then looks up the name and calls the function with `*numbers`, which spreads the
list into separate arguments.

## Code

```python
def register(registry, name):
    def decorate(func):
        if name in registry:
            raise ValueError(f"command already registered: {name}")
        registry[name] = func
        return func
    return decorate


def run_command(registry, line):
    parts = line.split()
    if not parts:
        raise ValueError("empty command")
    name = parts[0]
    if name not in registry:
        raise ValueError(f"unknown command: {name}")
    numbers = [int(word) for word in parts[1:]]
    return registry[name](*numbers)


COMMANDS = {}


@register(COMMANDS, "add")
def add(a, b):
    return a + b


@register(COMMANDS, "neg")
def neg(a):
    return -a


@register(COMMANDS, "total")
def total(*nums):
    return sum(nums)
```

## Complexity

Registering is O(1). `run_command` is O(length of the line) plus the command itself.

## Another way

Use the function's own name as the key: `registry[func.__name__] = func`, with a plain `@register` (no
arguments). That is shorter, but the explicit name lets the command word differ from the Python name
(for example `"sum"` without hiding the built-in `sum`).
