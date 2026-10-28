- Checking `isinstance(exc, ExceptionGroup)` only. A `BaseExceptionGroup` (for example one that
  holds a `KeyboardInterrupt`) is not an `ExceptionGroup`, so it would be treated as a leaf.
- Returning the path as a list or a string like `"1.1.0"`. The task asks for a tuple of ints.
- Only going one level deep. `ValueError("bad crc")` is two groups down.
- Calling `str()` on the leaves in `leaves`. It returns the exception objects; only `partition`
  returns messages.
- Forgetting that `split` can return `None`. `leaves(None)` raises the `TypeError` you wrote yourself.
- Writing your own matching with `type(exc) is exc_type`. Subclasses must match (`KeyError` is a
  `LookupError`), and so must tuples of types.
