## Walkthrough

Indices: `a0 b1 c2 d3 e4 f5`, length 6.

| Expression | Result | Why |
|---|---|---|
| `s[10:]` | `''` | the start is past the end; trimmed to empty |
| `s[-10:2]` | `ab` | -10 is trimmed to 0 |
| `s[4:1]` | `''` | forward from 4 never reaches 1 |
| `s[4:1:-1]` | `edc` | backwards from 4, stop before 1 |
| `s[::-2]` | `fdb` | from the end, every second |
| `s[-2::-2]` | `eca` | start at index 4, go back by 2 to the beginning |
| `s[1:4:-1]` | `''` | backwards from 1 never reaches 4 |
| `s[:2] + s[2:]` | `abcdef` | always the whole string |
| `s[::-1][1:3]` | `ed` | `fedcba`, then indices 1 and 2 |
| `len(s[::3])` | `2` | `ad` |
