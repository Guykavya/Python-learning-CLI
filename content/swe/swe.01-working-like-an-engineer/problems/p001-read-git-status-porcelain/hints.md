## Hint 1

Every line has the same shape: two characters, a space, then the path. What does `line[0]`, `line[1]` and `line[3:]` hold for ` M b.py`? Be careful: do **not** call `.strip()` on the whole line, because the leading space belongs to the status.

## Hint 2

A rename line looks like `R  old.py -> new.py`. The path part is everything after the 3rd character; if it contains ` -> `, take what is after it. A quoted path starts and ends with `"`.

## Hint 3

```text
result = four empty lists
for each non-blank line:
    x, y, path = line[0], line[1], line[3:]
    path: take the part after " -> " if present; remove surrounding quotes
    if line starts with "??": untracked.append(path); continue
    if x not in " ?":   staged.append(path)
    if y == "M":        modified.append(path)
    if "D" in (x, y):   deleted.append(path)
```
