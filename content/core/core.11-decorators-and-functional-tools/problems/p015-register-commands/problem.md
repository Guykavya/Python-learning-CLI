# @register: a command table built by decorators

A small calculator reads lines like `add 2 3`. Instead of a long `if name == "add": ... elif ...`, each
command function **registers itself** in a dict with a decorator. Many real tools (web routes, CLI commands,
test plugins) work like this.

Write in `solution.py`:

1. `register(registry, name)`: a decorator factory. Applied to a function, it stores the function in
   `registry[name]` and returns the function **unchanged** (no wrapper is needed). If `name` is already in
   the registry, raise `ValueError(f"command already registered: {name}")`.
2. `run_command(registry, line)`: split `line` on spaces. The first word is the command name, the rest are
   whole numbers. Call the registered function with those numbers as separate arguments and return its result.
   - Empty line: `ValueError("empty command")`.
   - Unknown name: `ValueError(f"unknown command: {name}")`.
3. A module-level dict `COMMANDS` with three commands registered by `@register(COMMANDS, ...)`:
   - `"add"`: `add(a, b)` returns `a + b`
   - `"neg"`: `neg(a)` returns `-a`
   - `"total"`: `total(*nums)` returns the sum of any number of values (0 for none)

**Examples**

```python
run_command(COMMANDS, "add 2 3")        # 5
run_command(COMMANDS, "neg 7")          # -7
run_command(COMMANDS, "total 1 2 3 4")  # 10
run_command(COMMANDS, "total")          # 0
run_command(COMMANDS, "mul 2 3")        # ValueError: unknown command: mul
add(10, 1)                              # 11  (still a normal function)
```
