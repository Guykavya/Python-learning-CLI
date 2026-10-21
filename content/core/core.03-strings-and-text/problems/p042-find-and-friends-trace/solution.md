## Walkthrough

Indices: `a0 -1 b2 -3 c4`.

| Expression | Result | Why |
|---|---|---|
| `find("-")` | `1` | first dash |
| `rfind("-")` | `3` | last dash |
| `find("-", 2)` | `3` | search starts at index 2 |
| `find("x")` | `-1` | not found |
| `s[s.find("x")]` | `c` | `s[-1]`, the trap: no error |
| `find("")` | `0` | the empty string is found at the first gap |
| `rfind("")` | `5` | the last gap, after `c` |
| `count("")` | `6` | one per gap, `len(s) + 1` |
| `count("-", 0, 2)` | `1` | only looks in `"a-"` |
| `"" in s`, `"" in ""` | `True True` | the empty string is in every string |
| `partition("x")` | `('a-b-c', '', '')` | not found: whole string first |
| `rpartition("-")` | `('a-b', '-', 'c')` | cut at the last dash |
