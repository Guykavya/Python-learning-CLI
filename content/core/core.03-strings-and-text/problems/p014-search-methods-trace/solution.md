## Walkthrough

Indices: `h0 e1 l2 l3 o4 _5 w6 o7 r8 l9 d10`.

| Line | Result | Why |
|---|---|---|
| `find("o")` | `4` | first o |
| `rfind("o")` | `7` | last o, counted from the left |
| `find("z")` | `-1` | not found |
| `count("l")` | `3` | at 2, 3 and 9 |
| `index("world")` | `6` | where the word starts |
| `replace("l", "L", 2)` | `heLLo world` | only the first two |
| `startswith("hell")` | `True` | |
| `endswith("World")` | `False` | capital W does not match |
| `"lo w" in s` | `True` | the substring spans the space |
| `upper().find("O", 5)` | `7` | the search starts at 5, skipping the O at 4 |
