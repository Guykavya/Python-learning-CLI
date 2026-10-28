- Saying A is "safer". It is stricter, but it rejects valid objects and protects against nothing the
  other versions do not also catch.
- Thinking `hasattr(target, "write")` proves that `write` works. It only proves the name exists; it
  could be an attribute that is not callable or that takes other arguments.
- Missing C's hidden bug. A big `try` around code you call turns *their* bugs into *your* misleading
  error message, and `from None` hides the evidence.
- Saying "EAFP means never check anything". It means: do the operation and handle the specific
  failure, in a small `try` block.
- Fixing `total` with `isinstance(numbers, (list, tuple))`. That still rejects `range` and generators.
  Check an ABC, or do not check at all.
- Saying "never use `isinstance`". It is the right tool for `str` vs list-of-`str`, for your own
  exception classes, and for clear validation at an API edge.
