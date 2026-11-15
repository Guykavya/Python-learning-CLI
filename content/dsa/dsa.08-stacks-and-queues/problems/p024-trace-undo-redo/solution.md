## Approach

Keep the full contents of both stacks on paper, not only their sizes. `type` is "save, change, clear redo"; `undo` and `redo` move one text between the stacks and the current text.

## Expected output

```text
type hi 'hi' 1 0
type _there 'hi_there' 2 0
undo 'hi' 1 1
type ! 'hi!' 2 0
undo 'hi' 1 1
undo '' 0 2
redo 'hi' 1 1
redo 'hi!' 2 0
redo 'hi!' 2 0
type ? 'hi!?' 3 0
redo 'hi!?' 3 0
undo 'hi!' 2 1
undo 'hi' 1 2
undo '' 0 3
```

## Why

| after | text | undo_stack | redo_stack |
|---|---|---|---|
| `type hi` | `'hi'` | `['']` | `[]` |
| `type _there` | `'hi_there'` | `['', 'hi']` | `[]` |
| `undo` | `'hi'` | `['']` | `['hi_there']` |
| `type !` | `'hi!'` | `['', 'hi']` | `[]` (cleared: `hi_there` is gone for good) |
| `undo`, `undo` | `''` | `[]` | `['hi!', 'hi']` |
| `redo`, `redo` | `'hi!'` | `['', 'hi']` | `[]` |
| `redo` | nothing to redo | | |
| `type ?` | `'hi!?'` | `['', 'hi', 'hi!']` | `[]` |
| `redo` | nothing to redo | | |
| `undo` x 3 | `''` | `[]` | `['hi!?', 'hi!', 'hi']` |

After the last line three `redo` commands would work, giving `'hi'`, `'hi!'`, `'hi!?'`. The text `'hi_there'` can never come back: typing `!` cleared the redo history.
