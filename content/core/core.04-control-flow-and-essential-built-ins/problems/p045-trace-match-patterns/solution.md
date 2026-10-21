## Walkthrough: commands

| Input | words | First matching case | Output |
|---|---|---|---|
| `go north` | `['go', 'north']` | guard true | `going north` |
| `go` | `['go']` | `["go"]` | `go where?` |
| `take red key` | 3 words | `["take", *things]` | `taking 2 things: ['red', 'key']` |
| `drop` | `['drop']` | the OR pattern for drop or throw | `drop what?` |
| (empty) | `[]` | `[]` | `empty` |
| `look around` | 2 words | `[verb, *_]` | `unknown verb look` |
| `GO west` | `['go', 'west']` | guard false, then `["go", other]` | `cannot go west` |

## Walkthrough: values

| Value | Output | Why |
|---|---|---|
| `0` | `0 -> nothing` | equal to 0 |
| `7` | `7 -> big int` | int and 7 > 5 |
| `"7"` | `'7' -> text` | a str, not an int |
| `2.5` | `2.5 -> other` | not an int, not a str, not a sequence |
| `None` | `None -> nothing` | `None` literal |
| `(1, 2)` | `pair 1 2` | sequence of length 2 |
| `3` | `3 -> other` | an int, but the guard `n > 5` is false |
