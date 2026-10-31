- Writing a literal space in a verbose pattern and expecting it to match a space. Verbose mode
  removes it. Use `[ ]`, `\ ` or `\s`.
- Writing `#` for a real hash in verbose mode. It starts a comment; use `\#` or `[#]`.
- Making brackets optional on their own, `\(?\d{3}\)?`. That accepts `(555 123-4567`.
- Using the same group name twice. Python raises `re.error: redefinition of group name`.
- Forgetting `re.VERBOSE` after laying the pattern out on lines. Then all the spaces, newlines
  and comments become part of the pattern and nothing matches.
- Returning the area as `'(555)'`. Strip the brackets.
- Using `re.match`/`re.search`. `call 555-123-4567` or a 6-digit extension slip through.
