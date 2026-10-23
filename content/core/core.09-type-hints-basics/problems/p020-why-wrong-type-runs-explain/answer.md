**1. Why it runs.** Python does not check hints. When it reads `width: float` it stores the hint
in `area.__annotations__` and moves on. At the call, nothing compares `"3"` with `float`. Hints are
notes for people and for other tools, not rules the interpreter enforces.

**2. Why `3333`.** The body is only `width * height`, and `"3" * 4` is perfectly legal: it repeats
the string four times, giving `"3333"`. This is more dangerous than a crash, because a crash points
at the problem, while a wrong value looks like a normal result and travels on through the program,
possibly into a file or a total, before anyone notices.

**3. What rejects it.** A **static** checker such as **mypy**. It reads the code *without running
it*, sees that `"3"` is a `str` where a `float` is expected, and reports `[arg-type]`. It does this
when I run `python -m mypy`, before the program runs; it is not part of the interpreter, and it
does nothing unless I run it. This is the difference between static and **runtime** checking.

**4. A check inside the function.** Add `isinstance` tests that raise `TypeError`. They belong at
the boundary where data enters (input, files, network); between my own annotated functions mypy is
enough.
