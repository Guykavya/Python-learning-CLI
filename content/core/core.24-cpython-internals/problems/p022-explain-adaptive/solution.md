## Approach

The model answer is in `answer.md`. The whole topic fits in one idea: **the interpreter bets that
the types it saw recently are the types it will see next**, rewrites the instruction to exploit
that bet, and protects the bet with a cheap guard.

| Stage | What `dis(adaptive=True)` shows | What happens |
|---|---|---|
| cold | generic names (`BINARY_OP`, `LOAD_ATTR`, `LOAD_GLOBAL`) | full, type-generic work every time |
| warmed up, stable types | specialised names (`BINARY_OP_ADD_INT`, `LOAD_ATTR_INSTANCE_VALUE`, `LOAD_GLOBAL_BUILTIN`) | one guard + fast path, data from inline caches |
| types changed | a different specialisation, or back to the generic name | guard fails -> generic path -> counter -> re-specialise after a back-off |

## Check your answer

- Did you say that the specialised instruction **assumes** something and checks it with a guard?
- Did you mention inline caches (`CACHE` entries) as the place where its data lives?
- Did you say that a failed guard still gives the **correct** result, just slower?
- Did you give one type-stable example that benefits and one that does not?
- Did you say that the names and warm-up thresholds are version details, and that this is not a
  JIT (no machine code)?

## Another way

Prove it to yourself with `timeit` (core.20): time `add(i, 1)` in a loop, then a loop that
alternates `add(i, 1)` and `add(1.5, 2.5)` and `add("a", "b")`. The second loop is slower per
call, partly because of the different types, partly because of failed guards. Then run
`dis.dis(add, adaptive=True)` after each experiment and compare. The numbers depend on your
machine and version, so compare the two loops with each other, never with someone else's numbers.
