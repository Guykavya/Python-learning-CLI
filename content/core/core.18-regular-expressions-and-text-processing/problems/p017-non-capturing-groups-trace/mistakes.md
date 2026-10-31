- Expecting `findall(r"(ab)+", ...)` to return `'ababab'`. With a capturing group, findall returns
  the group, and a repeated group keeps only its **last** repetition.
- Counting `(?:...)` as a group. It groups for `+` and `|` but is never numbered.
- Reading `red|green apple` as `(red|green) apple`. `|` splits the whole pattern unless brackets
  limit it.
- Writing `()` for a group that did not match. It is `None`, and `groups()` still has one
  entry per group: `(None,)`.
- Forgetting that a capturing group in `re.split` puts the separators in the result.
