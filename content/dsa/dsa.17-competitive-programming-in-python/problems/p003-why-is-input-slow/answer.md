## Model answer

**1. Work per call.** `input()` is a Python-level function. Every call looks up the global names, checks whether `sys.stdin` and `sys.stdout` are interactive terminals, **flushes** `sys.stdout` (so that a prompt would appear before waiting), reads a line, builds a new string and strips the newline. This is a fixed cost **per call**. Program A pays it 200 001 times.

**2. Buffering.** The operating system hands the program a block of bytes at a time (usually 4 to 64 KB), and Python's file object keeps that block in a **buffer**. So the data is already in memory; the slow part is not the disk but the many small steps around each line.

**3. `readline` and `read`.** `sys.stdin.readline()` skips the terminal checks and the flush, so it is faster per call but still runs 200 000 times and returns a string with the newline. `sys.stdin.read()` is **one** call: it returns the whole text, and `.split()` and `map(int, ...)` do the per-number work in C, not in Python bytecode.

**4. Size.** With `n = 10` the extra cost is microseconds. With `n = 2 * 10**5` the per-call overhead adds up to a visible part of a one-second limit; with `10**6` lines it can decide between "accepted" and "time limit exceeded".

**5. When line by line is needed.** Interactive problems (the judge answers only after your output) and inputs too big to hold in memory. Then use `sys.stdin.readline` (and `flush=True` when writing).

**Checklist: your answer should mention**
- [ ] a **fixed cost per call**, repeated `n` times
- [ ] **flush** and/or terminal checks inside `input()`
- [ ] the OS and Python **buffer** the data, so the disk is not the problem
- [ ] `readline` is lighter than `input`; `read().split()` is one call, work done in C
- [ ] it matters only for **large** `n`
- [ ] interactive problems still need line-by-line reading
