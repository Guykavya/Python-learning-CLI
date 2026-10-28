## Approach

Rewrite the call in the long form. `c.tick()` is `Counter.tick(c)` (chapter section 3), so `self` is
simply the first argument, and the object is always passed. Everything else, the error message, the
local-variable bug, and the reasons for being explicit, follows from that one fact.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Prove each claim in the REPL: `Counter.tick(c)` works like `c.tick()`; `c.tick` prints as
`<bound method Counter.tick of <...Counter object at 0x...>>` (the address differs on every machine);
`c.tick.__self__ is c` is `True`; and `vars(c)` after the buggy `__init__` is `{}`.
