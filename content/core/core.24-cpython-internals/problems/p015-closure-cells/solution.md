## Approach

Track cells, not values. A cell is created when the enclosing function is *called* (one per
cellvar per call), and every inner function made during that call keeps a reference to it.
Reading a free variable reads the cell's **current** content at the moment of the read.

| Line | Reasoning | Output |
|---|---|---|
| `make_counter` cellvars / freevars | `count` is assigned here and used by `step`; `make_counter` uses nothing from outside | `('count',) ()` |
| `step` freevars / cellvars | `step` reads `count` from the enclosing cell and owns no cells | `('count',) ()` |
| `__qualname__`, cell type | the qualified name records where `step` was defined; the cell's class is `cell` | `make_counter.<locals>.step cell` |
| `c(), c(), cell_contents` | arguments are evaluated left to right: 1, then 2, then the cell holds 2 | `1 2 2` |
| `d(), c(), is` | `d` has its own fresh cell (starts at 0), `c`'s cell goes 2 -> 3; two calls, two cells | `1 3 False` |
| after `cell_contents = 100` | writing the cell changes what `c` sees; `d`'s cell is separate (was 1) | `101 2` |
| `outer` cellvars | parameter `x` is needed by `inner`, so it lives in a cell | `('x',)` |
| `middle` freevars / cellvars | `middle` never reads `x`, but it must carry the cell down to `inner`, so `x` is free in `middle`; the cell belongs to `outer` | `('x',) ()` |
| `inner` freevars, contents | `inner` reads `x` from the same cell, which holds 5 | `('x',) 5` |
| module-level closures | `make_counter` and `outer` use no enclosing function's variables | `None None` |
| `make_adders` results | one `n` cell for the whole call; after the loop it holds 2; each lambda reads it when called | `[12, 12, 12]` |
| shared cell | all three lambdas hold the very same cell | `True 2` |
| fixed version | `n=n` evaluates `n` when each lambda is created and stores it as a default; `n` inside is a parameter, so no closure; the second lambda's default is 1 | `[10, 11, 12] None (1,)` |
| empty cell | `show` was created before `later` was assigned: the cell exists but is empty | `ValueError` |
| calling `show()` | reading an empty free variable is a `NameError` (for a plain local it would be `UnboundLocalError`) | `NameError` |
| after `later = "ready"` | assigning `later` fills the shared cell; both reads see it | `ready ready` |

## Full output

```
('count',) ()
('count',) ()
make_counter.<locals>.step cell
1 2 2
1 3 False
101 2
('x',)
('x',) ()
('x',) 5
None None
[12, 12, 12]
True 2
[10, 11, 12] None (1,)
ValueError
NameError
ready ready
```

## Complexity

Reading or writing a free variable is one extra pointer hop through the cell: O(1). The
bytecode uses `LOAD_DEREF` / `STORE_DEREF` for cell variables instead of `LOAD_FAST` /
`STORE_FAST` (opnames shown for interest; they are not part of the trace).

## Another way

Check yourself by adding prints of `[cell.cell_contents for cell in f.__closure__]` after each
step, or by running `dis.dis(make_counter)` and looking for the instruction that creates the
cell (`MAKE_CELL` on 3.11+). To avoid late binding without a default argument, create each
lambda in its own call, so each gets its own cell:

```python
def make_adder(n):
    return lambda x: x + n

adders = [make_adder(n) for n in range(3)]   # [10, 11, 12] when called with 10
```

`functools.partial(operator.add, n)` works too.
