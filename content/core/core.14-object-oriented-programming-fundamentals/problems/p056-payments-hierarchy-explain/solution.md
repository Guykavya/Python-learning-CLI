## Approach

Design the hierarchy from the **caller's** side (chapter section 17): which situations need different
handling? Each of those becomes a class that one `except` can catch. Put the data a caller needs into
attributes, and use chaining (chapter section 18) so that the low-level cause is kept for debugging
while the caller sees only `paykit`'s types.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Look at how real libraries do it. `requests` has `requests.RequestException` with `ConnectionError`,
`Timeout` and `HTTPError` below it; `HTTPError` keeps the `response` as an attribute. Several of
`requests`' classes also inherit from built-in ones (`IOError`, `ValueError`), the same choice as
point 6. Try `help(requests.exceptions)` if you have it installed, or write your `paykit` classes in a
file and call `issubclass(...)` on them to check the tree.
