## Hint 1

Sort the commands by "how far do I move": `s` (one step, may go **into** a call), `n` (one line
of **this** function), `r` (to the end of **this** function), `unt` (past this loop), `c` (to
the next breakpoint). Which distance does each situation want?

## Hint 2

Some situations are not about moving at all. Looking at callers: `w`, `u`, `d`. Stopping only
sometimes: `b LINE, CONDITION`. Repeated printing: `display`. After a crash: `pdb.pm()` or
`python -m pdb`. Turning `breakpoint()` off: an environment variable read by
`sys.breakpointhook`.

```
1 -> s     2 -> n, p total     3 -> r     4 -> b 88, <condition>
5 -> w, u, u     6 -> post-mortem     7 -> display x3     8 -> PYTHONBREAKPOINT=...
```
