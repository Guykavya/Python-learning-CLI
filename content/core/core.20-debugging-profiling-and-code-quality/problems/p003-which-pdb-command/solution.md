## Approach

The model answer is in `answer.md`. The idea behind it: pdb commands fall into four groups,
and each situation needs one group.

| Group | Commands | Question it answers |
|---|---|---|
| Move | `s`, `n`, `r`, `unt`, `c` | "run how far before stopping again?" |
| Look | `p`, `pp`, `ll`, `l`, `w`, `args`, `display` | "what is the state right now?" |
| Change view | `u`, `d` | "show me the caller's (or callee's) variables" |
| Control stops | `b`, `b LINE, COND`, `condition`, `cl`, `PYTHONBREAKPOINT` | "where and when should it stop?" |

## Check your answer

- Did you separate `s` (goes into calls) from `n` (steps over them)?
- Did you use `r` (finish this function), not `c`, to get out of a helper?
- Did you put the condition **on the breakpoint** instead of editing the code?
- Did you say that `u`/`d` change only what you *look at*, not where the program is?
- Did you name a real post-mortem tool (`pdb.pm()`, `python -m pdb`)?
- Did you turn `breakpoint()` off with `PYTHONBREAKPOINT=0` rather than deleting lines?

## Another way

VS Code gives the same tools as buttons: Step Into (`s`), Step Over (`n`), Step Out (`r`),
Continue (`c`), a Call Stack panel (`w`, `u`, `d`), Watch expressions (`display`) and
conditional breakpoints (right-click a breakpoint, "Edit Condition"). Knowing the pdb names
helps on servers and in terminals where there is no editor.
