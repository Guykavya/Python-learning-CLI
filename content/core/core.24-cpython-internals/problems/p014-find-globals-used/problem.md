# Which globals does a function use?

Linters such as pyflakes report "undefined name `lenn`" without running your code. One way to
do that is to read the bytecode: when a function reads a name that is not a local and not a
closure variable, the compiler emits a **`LOAD_GLOBAL`** instruction, and its `argval` is the
name. That instruction name has been the same on every version since 3.11 (the most stable
opname you will meet), and `argval` is always the plain name, even though the raw `arg`
number is encoded differently from version to version.

Do not use `func.__code__.co_names` for this. It holds every name the code uses *by name*:
globals, but also attribute names (`p.x` puts `"x"` there), method names and names assigned
with `global`.

Copy `starter.py` to `solution.py` and write two functions.

**`globals_used(func)`** returns a **sorted list without duplicates** of the names that `func`
loads as globals or builtins: the `argval` of every instruction whose `opname` is exactly
`"LOAD_GLOBAL"` in `dis.get_instructions(...)`. Also look inside every nested code object
(inner functions, lambdas, generator expressions) found in `co_consts`, at any depth.

**`undefined_globals(func)`** returns the sorted names from `globals_used(func)` that are
neither keys of `func.__globals__` (the module the function was defined in) nor names in the
`builtins` module. These are probably typos.

**Example**

```python
import math

RATE = 0.2

def price(item):
    return round(item.cost * (1 + RATE) + math.sqrt(4), 2)

def report(items):
    def line(i):
        return f"{i.name}: {price(i)}"
    return [lenn(items)] + [line(i) for i in items]

globals_used(price)        # ['RATE', 'math', 'round']   (not 'cost', not 'sqrt')
globals_used(report)       # ['lenn', 'price']           ('price' is used by the inner function)
undefined_globals(report)  # ['lenn']
```

**Version note.** A few names never appear as `LOAD_GLOBAL`. For example, the
`AssertionError` raised by an `assert` statement is loaded by a special instruction whose name
changed between versions. Your function only needs to report what `LOAD_GLOBAL` loads.
