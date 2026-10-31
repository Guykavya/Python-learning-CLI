- Using `n` to get into a function. `n` treats the whole call as one step.
- Using `c` to leave a helper. It runs to the next breakpoint, which may be nowhere (the
  program just finishes).
- Writing `if row["id"] == 4071: breakpoint()` into the code. It works, but you have to edit,
  re-run and remember to delete it; a conditional breakpoint does the same from the prompt.
- Thinking `u` runs code backwards. It only changes which frame `p` and `ll` look at.
- Re-running the whole program with `breakpoint()` added after a crash, when `pdb.pm()` could
  open the crashed frame directly.
- Commenting out every `breakpoint()` by hand. `PYTHONBREAKPOINT=0` switches them all off.
