See the model answer shown when you check. The ideas that must appear:

1. At least six concrete edge cases with expected outputs: `n = 0`, `n = 1`, all negative, all
   equal, very large values, a mix with zero, negative `n`.
2. `n = 0` crashes with `ZeroDivisionError`; starting `largest`/`smallest` at 0 gives a value that is
   not in the input when all numbers are negative (or all positive); the fix is to start from the
   first value read.
3. Choosing tests: boundaries of every limit, smallest/largest values, just inside and just outside,
   special shapes, and expected outputs worked out by hand first.
4. A short reusable checklist.
