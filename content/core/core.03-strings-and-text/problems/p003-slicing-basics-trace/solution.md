## Walkthrough

`s = "computer"` has length 8: `c0 o1 m2 p3 u4 t5 e6 r7`.

| Expression | Result | Why |
|---|---|---|
| `s[0:3]` | `com` | indices 0, 1, 2 |
| `s[3:]` | `puter` | from 3 to the end |
| `s[:-3]` | `compu` | everything except the last three |
| `s[-3:]` | `ter` | the last three |
| `s[2:6]` | `mput` | indices 2 to 5 |
| `s[::2]` | `cmue` | indices 0, 2, 4, 6 |
| `s[::-1]` | `retupmoc` | reversed |
| `s[1:100]` | `omputer` | the stop is trimmed to 8, no error |
| `len(s[4:4])` | `0` | start equals stop, so it is empty |
| `s[-5:-2]` | `put` | same as `s[3:6]` |

## The rule

`s[a:b]` has `b - a` characters when both are in range, and a negative index means "add the length".
