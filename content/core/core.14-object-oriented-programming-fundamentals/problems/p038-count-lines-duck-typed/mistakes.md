- Checking `isinstance(source, list)` (or `hasattr(source, "readlines")`). Generators and custom
  classes then fail, although they give lines perfectly well.
- Calling `source.readlines()` or `source.read()`. Lists and generators do not have them.
- Forgetting the `str` check. `count_nonblank("ab\n")` then counts characters and returns 2.
- Calling `list(source)` in `first_line` before searching. That reads everything, and on an
  endless source it never finishes.
- Making `Lines` its own iterator (`__iter__` returns `self` with a position counter) without
  resetting. The second loop then gives nothing.
- Checking the comment on the raw line: `"   # note"` does not start with `"#"` until you strip it.
