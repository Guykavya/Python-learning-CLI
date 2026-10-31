- Greedy `\[(.*)\]\((.*)\)`: on a line with two links, `.*` runs to the **last** `]` and `)`, and
  both links become one broken link.
- Forgetting to escape `[`, `(`: `[(.*)]` is a character class, not brackets.
- Writing the replacement as a normal string `'<a href="\2">'`: `"\2"` in a normal string is the
  character with code 2. Use a raw string.
- Matching the `!` with `[^!]\[` instead of a lookbehind: that consumes the character before the
  link (it disappears from the output) and fails for a link at the very start of the text.
- Allowing spaces between `]` and `(`, or inside the url.
- Using `*` instead of `+`, so `[](x)` becomes an empty link.
