## Approach

Keep two questions apart for every line: *what does the call return* and *does anything print
by itself*. Only `"single"` mode prints on its own, through `sys.displayhook`, the same hook
the REPL uses to show `>>> 40 + 2` as `42`.

| Code | Reasoning | Output |
|---|---|---|
| `type(expr).__name__, co_name, co_filename` | compile returns a `code` object, always named `<module>`; the filename is the label we gave | `code <module> <calc>` |
| `eval(expr, ...)` twice | the same code runs with different globals: `21 * 2` and `"ab" * 2` | `42 abab` |
| `print(exec(prog, ns))` | `exec` runs the statements and returns `None` | `None` |
| `ns["y"], ns["z"], "__builtins__" in ns` | the assignments went into `ns`; `exec` added `__builtins__` | `10 15 True` |
| `prog.co_name, sorted(prog.co_names)` | module-level names are stored by name, so `y` and `z` are in `co_names` | `<module> ['y', 'z']` |
| `eval(as_exec, ...)` | in exec mode `x * 2` is an expression *statement*: computed, then discarded | `None` |
| `compile("y = 10", ..., "eval")` | an assignment is not an expression, so compiling fails | `SyntaxError <bad>` |
| `exec(single)` | single mode prints the value of the expression statement | `42` |
| `print("result:", result)` | ...and `exec` still returns `None` | `result: None` |
| last block | `exec` of a string, with an existing dict; the list is sorted in place | `[1, 2, 3] 3` |

## Full output

```
code <module> <calc>
42 abab
None
10 15 True
<module> ['y', 'z']
None
SyntaxError <bad>
42
result: None
[1, 2, 3] 3
```

## Complexity

Compiling is linear in the source size; each code object here runs a handful of instructions.

## Another way

Check the modes in the REPL with `compile(..., "single")` and `dis.dis`: the single-mode code
ends with a call to the display hook (the instruction name differs between versions, so read it,
do not memorise it). Because `compile` is separate from running, you can compile once and
`eval` many times with different namespaces, which is how template engines and calculators
avoid re-parsing.
