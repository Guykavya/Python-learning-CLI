# Spot constant folding

When the compiler sees an expression made only of literals, it computes the result **once, at
compile time**, and stores the answer as a constant. This is **constant folding**:

```python
code = compile("24 * 60 * 60", "<expr>", "eval")
86400 in code.co_consts          # True: the multiplication never runs at run time
```

Similar tricks: a tuple of literals becomes one tuple constant, and in `x in [1, 2, 3]` the
list (which nobody can change) becomes the constant tuple `(1, 2, 3)`, a set display after `in`
becomes a `frozenset`. Anything involving a name or a call, like `len("abcd") * 1000` or
`x * 60`, cannot be folded: the compiler does not know what `len` or `x` will be.

Copy `starter.py` to `solution.py` and write two functions.

**`all_constants(source, mode="exec")`** compiles `source` with `compile(source, "<src>", mode)`
and returns a list of every constant in that code object's `co_consts` **and in every nested
code object**, at any depth (a `def`, `class` or `lambda` inside the source has its own code
object, which appears inside `co_consts`). Code objects themselves are not included in the
result. Order does not matter.

**`is_folded(expr, value)`** returns `True` if compiling `expr` in `"eval"` mode produced a
constant equal to `value` **and of the same type** (so `1000.0` does not count as `1000`).

**Example**

```python
is_folded("24 * 60 * 60", 86400)              # True
is_folded("x in [1, 2, 3]", (1, 2, 3))        # True: the list became a tuple constant
is_folded("len('abcd') * 1000", 4000)         # False: calls are never folded
is_folded("2.0 * 500", 1000)                  # False: the folded value is the float 1000.0

src = "def seconds_per_week():\n    return 7 * 86400\n"
604800 in all_constants(src)                  # True: found in the nested function's code
```

**Version warning.** What gets folded and which *extra* constants stay in `co_consts` changes
between versions. For example, 3.14 may keep an operand such as `24` in `co_consts` next to the
answer, and loads small ints (0 to 255) with a special instruction so they may not be in
`co_consts` at all. So only ever ask "is the folded answer there?", and only for values that are
not small ints.
