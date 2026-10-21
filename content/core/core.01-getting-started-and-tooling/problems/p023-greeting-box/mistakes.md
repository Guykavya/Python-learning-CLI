- Using `len(name)` instead of the length of the whole message. The box comes
  out 8 characters too narrow.
- Forgetting the `+ 2` for the padding spaces.
- Using `print("|", message, "|")`: `print` adds spaces itself, which happens to
  give one space each side here, but mixing that with `+` elsewhere often
  produces off-by-one boxes. Be consistent.
- Trailing spaces are invisible: the empty line must end with `|`, so its spaces
  are counted.
