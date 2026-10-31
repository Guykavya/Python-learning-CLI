- Fixing only the greedy `.+` with `.+?`. The lazy version stops early but can still cross
  spaces when needed, and the other four bugs remain.
- Escaping the dot but keeping one label: `@[\w-]+\.[a-z]+` misses `mail.co.uk` (it returns
  `r@mail.co`).
- Adding a capturing group around the labels, `([A-Za-z0-9-]+\.)+`. `findall` then returns
  `'co.'` instead of the address. Use `(?:...)`.
- Lower-casing the text before searching. The addresses must come back spelled as written.
- Forgetting `\b` at the end, so `bob@site.com2` yields `bob@site.co`.
- Putting `\b` at the start too, `\b[\w.%+-]+@`. That breaks a local part that starts with `.`
  or `%`; the class already stops at characters that cannot belong.
