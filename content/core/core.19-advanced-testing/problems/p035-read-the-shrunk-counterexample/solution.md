## Approach

Treat the report as a small investigation:

1. Which property failed? "Joining the pieces gives the items back" is about **everything arriving**, and the result `[] == [0]` shows that nothing did.
2. Hypothesis found a failing input and **shrank** it to the smallest one: a single item. A tiny failing input is almost the whole diagnosis.
3. The empty list is not a failure (an empty result is right for it), so one item is the minimum. The size does not matter (`or any other generated value`), so the bug is
   in how the list length is used, not in the size.
4. Trace by hand: `range(0, len(items) - size, size)` stops before the last start index. The correct stop is `len(items)`.

See `answer.md` for the full model answer.

## Complexity

Not applicable. The corrected function is O(n): one slice per piece.

## Another way

You can reproduce the shrunk case yourself in a plain test: `assert chunk([0], 1) == [[0]]`. Keep it as a regression test: hypothesis can find the bug again by itself, but a named example
documents *why* the code looks the way it does and still runs if someone later turns hypothesis off. With `database=None` hypothesis does not remember failures between runs, so the
example test is your memory.
