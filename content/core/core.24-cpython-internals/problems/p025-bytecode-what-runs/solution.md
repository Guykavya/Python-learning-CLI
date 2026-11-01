## Approach

Answer each question from the right object: the **code object** for what the compiler decided
(names, constants, flags), the **frame** for what is happening now (line, variables, caller).

## Trace

**`measure`'s code object.**

- `co_name` is `measure`, `co_argcount` is 2 (`b` is a normal positional parameter with a
  default). `co_varnames`: parameters `a`, `b`, then locals in order of appearance:
  `first`, `total`, `label`, `second`.
- The compiler folds `"ab" * 3` into `"ababab"` before it fills `co_consts`, so `"ab"` is not
  there: `True False`. The docstring is a constant too: `True`.
- `co_names` holds the names looked up by name at run time: only the global `where` →
  `('where',)`.
- `measure(5)`: the two `where()` calls are three lines apart, `total = 7`, `label = 'ababab'` →
  `(3, 7, 'ababab')`.

**The generator.**

- `countdown(2)` runs no code; the frame exists but is not started: `GEN_CREATED False`.
- First `next`: the body runs to the `yield` and pauses: `2 GEN_SUSPENDED`. The frame keeps
  `n == 2` and its line is the `yield` line, two below the `def`: `2 2`.
- Second `next`: `n -= 1`, loop, yield 1. Then `f_locals["n"]` is read: `1 1`.
- Third `next`: `n` becomes 0, the loop ends, `return "done"` raises `StopIteration` with
  `value == "done"`: `stop done`.
- A finished generator drops its frame: `GEN_CLOSED True`.
- The compiler marks generator functions with the `CO_GENERATOR` flag: `True False`.

**Nested code, frame chain, snapshot.**

- `make_helper`'s constants contain exactly one code object, `helper`'s, whose qualified name
  is `make_helper.<locals>.helper`: `1 helper make_helper.<locals>.helper`.
- `1000` is needed only by `helper`'s bytecode: `False True`.
- `inner`'s frame, its `f_back` (`outer`), and that one's `f_back` (the module):
  `['inner', 'outer', '<module>']`.
- `dict(...)` copies the variables while `x == 1`; the later `x = 2` does not change the copy:
  `(1, 2)`.

```
measure 2 ('a', 'b', 'first', 'total', 'label', 'second')
True False True
('where',)
(3, 7, 'ababab')
GEN_CREATED False
2 GEN_SUSPENDED
2 2
1 1
stop done
GEN_CLOSED True
True False
1 helper make_helper.<locals>.helper
False True
['inner', 'outer', '<module>']
(1, 2)
```

**Why these lines are version-proof.** The program avoids every fact that changed between 3.11
and 3.14: small ints such as `2` or `3` are not stored in `co_consts` on 3.14 (it has a
`LOAD_SMALL_INT` instruction), `None` may or may not be a constant, list, set and dict comprehensions
stopped having their own code object in 3.12 (PEP 709), and `f_locals` became a live write-through view in 3.13 (PEP 667).
`1000`, strings, names, flags, line differences and a `dict()` copy behave the same everywhere.

## Another way

Run `dis.dis(measure)` and `dis.dis(make_helper)` on your Python: you will see `LOAD_GLOBAL where`,
`LOAD_CONST 'ababab'` and the nested `<code object helper ...>`. The opcode names differ between
versions, but the constants and names they refer to are the same ones this trace printed.
