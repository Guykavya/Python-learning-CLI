**1. What the engine tries.** Python's `re` is a backtracking engine: when a later part of the
pattern fails, it goes back and tries another choice it skipped earlier. In `(a+)+b` there are two
choices: how many `a`s the inner `a+` takes, and how many times the outer `+` repeats. On
`"aaaac"` it first puts all four `a`s in one group, then fails at `c` (needs `b`). So it tries
`aaa|a`, then `aa|aa`, `aa|a|a`, `a|aaa`, ... every way to cut the run into groups. Between `n`
letters there are `n - 1` gaps and each gap is either a cut or not, so there are **2^(n-1)** ways.
Every one of them fails at the same `c`, and only after trying them all does the engine give up
(and then `search` starts again at the next position, which adds even more). Two more letters mean
four times as many splits: the timings grow about 4x per +2 (0.0076 → 0.0296 → 0.1135 → 0.4445 →
1.8056 s). That is exponential: 30 letters would take minutes, 40 would take days.

**2. Why the matching input is fast.** On `"a"*24 + "b"` the first try already works: one group
of all the `a`s, then `b`. A successful match ends the search, so none of the other splits are ever
tried. Backtracking only explodes when the overall match **fails** after a long run that can be
split in many ways. That is why such bugs pass all the normal tests and appear in production.

**3. The rewrite.** `a+b` matches exactly the same strings: "one or more groups of one or more
`a`" is just "one or more `a`". Now there is only one choice (how many `a`s), so a failure is
detected after at most `n` steps per start position. Python 3.11+ also has **atomic groups**
`(?>a+)+b` and **possessive quantifiers** `(a++)+b`: once the group has matched, the engine is not
allowed to go back into it and try other splits, so the failure is found quickly.

**4. Spotting it.** Dangerous shapes:
- a quantifier inside a quantifier where the inside can match the same text in several ways:
  `(a+)+`, `(\w+\s?)*`, `(x*)*`;
- alternatives that overlap, repeated: `(a|aa)*`, `(\w|\d)+`;
- several neighbouring quantifiers that can share text: `\d+\d+\d+x` (polynomial rather than
  exponential, but still slow on long input).
The fix is to make each character matchable in only **one** way.

Defences for user input: rewrite the pattern so there is no ambiguity (or use atomic/possessive
forms), and **limit the input length** before matching (a 200-character cap turns minutes into
nothing for many patterns). Where the job is really parsing, use a real parser or plain string
methods instead of a regex. `re` has no timeout, so the pattern itself must be safe.
