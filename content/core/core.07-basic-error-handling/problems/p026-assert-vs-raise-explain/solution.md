See the model answer shown when you check. The ideas that must appear:

1. `-O` strips asserts: `pay(100, "-50")` gives 150 and `pay(100, "500")` gives -400, silently.
2. `assert` states programmer invariants and may be disabled; input checks need `if ... raise`.
3. Both input checks become `raise ValueError(...)` with messages that say what to do; the
   non-number case is translated into a clear `ValueError`; the final check may stay an `assert`.
4. `AssertionError` is the wrong signal: callers catch `ValueError` for bad input.
5. `assert (cond, "msg")` asserts a non-empty tuple, which is always true.
