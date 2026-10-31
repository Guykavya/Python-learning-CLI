- `line.split(",")`: breaks quoted fields that contain commas.
- `re.findall(r'"[^"]*"|[^,]+', line)`: skips empty fields entirely (`[^,]+` needs at least one
  character), and keeps the quotes.
- A pattern that can match the empty string, used without `(?:^|,)`: `finditer` finds an extra
  empty match at the very end, so `a,b` gives `['a', 'b', '']`.
- A greedy plain field `[^,]*`: it swallows the trailing spaces, so `" x , y"` gives `'x '`.
  Either use the lazy `*?` with `\s*` after it, or `.strip()` the plain value.
- Testing `if m.group("quoted"):` instead of `is not None`: an empty quoted field `""` is falsy and
  falls into the plain branch, where the group is `None`.
- Forgetting to turn `""` into `"` inside quoted values.
