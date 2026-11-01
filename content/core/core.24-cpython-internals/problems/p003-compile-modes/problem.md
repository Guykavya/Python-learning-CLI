# Trace: compile, eval and exec

`compile(source, filename, mode)` turns text into a **code object** without running it. The
`mode` says what kind of text it is:

| Mode | Accepts | Running it gives |
|---|---|---|
| `"eval"` | a single **expression** | `eval(code)` returns the expression's value |
| `"exec"` | any number of **statements** | `exec(code)` runs them and returns `None` |
| `"single"` | one interactive statement | like `exec`, but an expression's value is **printed** (what the REPL does) |

`eval` and `exec` accept a code object or a string, plus an optional dict to use as the global
namespace. If that dict has no `"__builtins__"` key, Python adds one so the code can still use
`len`, `print` and friends. The code object made by `compile` is always named `"<module>"`, and
`filename` is just a label stored in `co_filename` (it shows up in tracebacks).

Work out, line by line, exactly what this program prints. The program needs no input.

```python
expr = compile("x * 2", "<calc>", "eval")
print(type(expr).__name__, expr.co_name, expr.co_filename)
print(eval(expr, {"x": 21}), eval(expr, {"x": "ab"}))

prog = compile("y = 10\nz = y + 5", "<prog>", "exec")
ns = {}
print(exec(prog, ns))
print(ns["y"], ns["z"], "__builtins__" in ns)
print(prog.co_name, sorted(prog.co_names))

as_exec = compile("x * 2", "<calc>", "exec")
print(eval(as_exec, {"x": 21}))

try:
    compile("y = 10", "<bad>", "eval")
except SyntaxError as e:
    print(type(e).__name__, e.filename)

single = compile("40 + 2", "<one>", "single")
result = exec(single)
print("result:", result)

namespace = {"items": [3, 1, 2]}
exec("items.sort()\nsize = len(items)", namespace)
print(namespace["items"], namespace["size"])
```

Write your answer in `answer.txt`, one output line per line of output.

**Example (a different program)**

```python
code = compile("a + b", "<sum>", "eval")
print(eval(code, {"a": 1, "b": 2}), code.co_filename)
```

prints

```
3 <sum>
```
