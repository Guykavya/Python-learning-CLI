**1. The styles.** Version A is **LBYL**, "Look Before You Leap": it checks whether the operation
will work before doing it. Version B is **EAFP**, "Easier to Ask Forgiveness than Permission": it
does the operation and handles the exception if it fails.

**2. Inputs where they differ.**

| Input | A (`isdigit` check) | B (`try int`) |
|---|---|---|
| `"-5"` | `None` (`-` is not a digit) | `-5` |
| `" 7"` | `None` (space is not a digit) | `7` (int strips whitespace) |
| `"+3"` | `None` | `3` |
| `"1_000"` | `None` | `1000` (underscores between digits are allowed) |
| `"²"` | **crashes**: `"²".isdigit()` is `True`, then `int("²")` raises `ValueError` | `None` |

The underlying problem: `isdigit` answers "are all these characters digit characters?", but the
real question is "can `int` convert this?". The only check that matches `int`'s rules exactly is
calling `int`. (Whether `-5` should be accepted as a quantity is a separate rule; it should be
checked with an explicit `if quantity <= 0`, not by accident through `isdigit`.)

**3. The race.** The file can be deleted, renamed or have its permissions changed **between** the
`exists` check and the `open` call, by another program, another user, or another part of the same
system. The check was true when it ran and false a moment later. This is a **race condition**,
called "time of check to time of use": the two steps are not one atomic action. It happens rarely,
so it is very hard to reproduce. The EAFP version has no gap:

```python
try:
    f = open(name)
except FileNotFoundError:
    print(f"Could not find {name!r}. Check the file name and try again.")
```

The failure is detected at the exact moment of use, by the operation itself. (The check also
cannot cover every failure: a file that exists may still be unreadable, which raises
`PermissionError`.)

**4. When LBYL is better.**

- When the check is **simple, cheap and exactly right**, and reads more clearly: `if not marks:`
  before computing an average, `if amount <= 0:` before a payment.
- When failure is **common**: raising and catching an exception costs more than an `if`, so in a
  hot loop where half the keys are missing, `if key in d` (or `d.get`) is faster and clearer.
- When an action **cannot be undone halfway**: validate all the inputs first, then change
  anything, so a failure leaves no half-finished state (for example checking every transfer before
  moving any money).

Key ideas to check: correct names and mapping; isdigit misses signs, spaces and underscores;
`"²"` passes isdigit and crashes int; the time gap between check and use; EAFP detects the failure
at the moment of use; LBYL wins for simple exact checks, common failures, or all-or-nothing work.
