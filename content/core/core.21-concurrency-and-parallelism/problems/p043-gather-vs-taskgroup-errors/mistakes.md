- Thinking plain `gather` cancels the other tasks when one fails. It does not; `c done` still
  appears, after `caught`.
- Putting `c done` before `caught ValueError('b')`. `c` needs 0.03 s; the error arrives at 0.02.
- Printing `caught ValueError('b')` in part 2. With `return_exceptions=True` nothing is raised;
  the error is an item of the list.
- Writing the list as `['d', 'e', 'f']` or `['d', ValueError, 'f']`. The slot holds the
  exception **instance**, shown with its `repr`: `ValueError('e')`.
- Printing `i done` in part 3. The TaskGroup cancelled `i` at 0.02, before its 0.03 s were up.
- Printing `after the block`. The `async with` block ended by raising the group, so the next
  line inside the `try` is skipped.
- Writing `caught ValueError ['h']`. `except*` gives you an `ExceptionGroup` (holding only the
  matching exceptions), never a bare `ValueError`.
