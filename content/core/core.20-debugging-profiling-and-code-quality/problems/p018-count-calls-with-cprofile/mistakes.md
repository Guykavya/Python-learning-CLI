- **Using `primitive_calls`.** For recursive code it counts only the outer call: `fib` shows `1`
  instead of `177`. The printed `ncalls` column `177/1` is "total/primitive".
- **No `finally`.** If `fn` raises, `disable()` is skipped. In Python 3.12+ the next
  `enable()` then fails with "Another profiling tool is already active".
- **Catching the exception to "be safe".** `except Exception: pass` hides the error from the
  caller. Use `try/finally`, not `try/except`.
- **Keeping one profiler at module level.** Its counts add up across calls, so the second answer
  is wrong.
- **Keying by the whole `(filename, line, name)` tuple or overwriting with `=`.** The task asks
  for names, and same-named functions must be added together.
- **Parsing the printed report text.** `print_stats()` output is for humans and its layout
  changes; the `.stats` dictionary is the data.
