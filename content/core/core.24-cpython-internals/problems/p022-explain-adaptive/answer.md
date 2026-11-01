**1. Warming up and specialising.** Generic `BINARY_OP (+)` works for any two objects: at every
execution it checks the types and finds the right `__add__`. After an instruction has run a few times
("warmed up"), the interpreter replaces it by a **specialised** instruction that fits what it has
seen. (`RESUME` -> `RESUME_CHECK` is a similar swap, a 3.13+ detail.)
`BINARY_OP_ADD_INT` assumes both operands are `int`: it does one cheap type check (a *guard*)
and adds directly, skipping the general lookup. What it saw and needs (counters, a cached
version tag of a type or a dict, an attribute's index) lives in **inline caches**: the `CACHE`
entries that follow the instruction in the bytecode, hidden by `dis` unless you pass
`show_caches=True`. The bytecode is rewritten in place; the meaning of the program never changes.

**2. Guards fail: deoptimise.** With floats, the guard of `BINARY_OP_ADD_INT` fails. The
instruction then behaves like the generic `BINARY_OP` (the result is still correct), and a counter
records the miss. After enough misses it goes back to the adaptive form and, after a back-off
delay, re-specialises for what it sees now: `BINARY_OP_ADD_FLOAT`. The cost is the failed checks
plus the slower generic path until it settles. If the types keep changing, it keeps falling back
and the function stays at roughly pre-3.11 speed.

**3. Type stability.** A hot loop such as `total += x` over a list of ints, or `p.x` on objects
of one class, keeps the same types every time, so each instruction stays specialised and runs its
fast path millions of times (`FOR_ITER_LIST`, `BINARY_OP_ADD_INT`, `LOAD_ATTR_INSTANCE_VALUE`).
Code where one line sees ints, floats, strings and different classes in turn, for example a
generic `sum` over a mixed list or a function called on many unrelated types, gets little benefit.
Code that spends its time inside C functions (`sorted`, regex, numpy) also barely changes, because
the bytecode is not the bottleneck.

**4. Observing it.** `dis.dis(func, adaptive=True)` (3.11+) after calling the function shows the
specialised names; `dis.get_instructions(func, adaptive=True)` gives the same as data. Everything
about it is a CPython implementation detail: the instruction names, how many calls warm-up takes and
which cases are specialised all change between versions, so never test against them. It is **not**
a JIT: no machine code is generated, it still interprets bytecode, just more specific bytecode.
The experimental JIT in 3.13+ is a separate, later stage that can compile hot traces of this
specialised code to machine code.
