## Hint 1

Split the program into four questions and answer each with one idea:

1. **The code object of `measure`** is fixed at compile time. Which names are local (assigned
   or parameters), and which one is looked up as a global? Which literal values does the bytecode
   need *after* folding: is `"ab"` still needed once `"ab" * 3` has been folded?
2. **The frames during `measure(5)`.** `where()` reports the line its *caller* is on. How many
   lines apart are the two calls?
3. **The generator's frame.** Before the first `next()`, has the body run at all? Where is the
   frame paused after the first `yield`, counted from the `def` line? What does a generator do
   with its frame once it returns?
4. **Nested code, frame chains, snapshots.** Which code object contains the constant `1000`: the
   one of `make_helper` or the one of `helper`? What does `f_back` point to, twice? Does a copy
   made with `dict()` see a later assignment?

## Hint 2

```
measure:   varnames = (a, b, first, total, label, second); names = (where,)
           consts contain the docstring and the folded 'ababab' (the pieces are gone)
           second - first = 3 lines; total = 5 + 2; label = 'ababab'
countdown(2):
    created     -> state GEN_CREATED, frame exists (gi_frame is not None)
    next -> 2   -> GEN_SUSPENDED, paused at the yield line = def line + 2, n == 2
    next -> 1   -> n == 1 (next() runs before f_locals is read)
    next        -> loop ends, return "done" -> StopIteration.value == "done"
    afterwards  -> GEN_CLOSED and gi_frame is None
CO_GENERATOR flag: set for countdown, not for measure
make_helper: one code object in its consts (helper); 1000 lives in helper's consts
inner -> outer -> <module>
snapshot: copy taken while x == 1, so (1, 2)
```
