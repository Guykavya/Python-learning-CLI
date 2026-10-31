- `lines.index("")` and slicing: fails on a generator (no `index`, no slicing).
- Calling `takewhile(..., lines)` and then `dropwhile(..., lines)` on a generator: the first call
  already used up the lines, so the second sees only the rest.
- Expecting the blank line at the start of the body: `takewhile` has already consumed it.
- `line.split(":")` without a limit: `Time: 10:30` has two colons and the unpacking fails.
- Stripping the body lines: the body must stay unchanged.
