- Using `sys._getframe()` (frame 0). That is the hook itself; you would record `'hook'` and its
  arguments.
- Storing `frame.f_locals` without `dict(...)`. Old records then change when the variables
  change (a proxy in 3.13+, a reused dict before).
- Defining the hook as `def hook():`. `breakpoint("x")` then fails with `TypeError`.
- Creating `records` once at module level. A second `install_recorder()` would keep appending to
  the old list.
- Calling `breakpoint()` inside the hook, or calling the old hook from it: that starts the real
  debugger and waits for keyboard input.
- Restoring with `sys.breakpointhook = None` or `del sys.breakpointhook`. The original is kept
  in `sys.__breakpointhook__` for exactly this purpose.
