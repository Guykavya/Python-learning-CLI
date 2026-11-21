# The status flow

Chapter sections 2.1 (rule 4: the status flow), 8.3 and 8.5 (every status move tested). The allowed moves of a task are a small **state machine**: three statuses and four actions. Write the table once, and a function that follows it.

| Action | From | To |
|---|---|---|
| `start` | `todo` | `doing` |
| `pause` | `doing` | `todo` |
| `finish` | `doing` | `done` |
| `reopen` | `done` | `todo` |

Everything else is not allowed. For example `todo -> done` (finish a task that was never started) and `done -> doing` do not exist.

## What to write

```python
class RuleViolation(Exception): ...        # given

STATUSES = ("todo", "doing", "done")       # given
ACTIONS = ("start", "pause", "finish", "reopen")   # given

def next_status(current: str, action: str) -> str: ...
```

- `next_status(current, action)` returns the new status when the move is in the table.
- If the move is **not** in the table it raises `RuleViolation` whose message **names both** the current status and the action (for example `cannot finish a task that is todo`).
- If `current` is not one of `STATUSES` or `action` is not one of `ACTIONS` it raises `ValueError` (that is a programmer's mistake, not a business outcome).
- Keep the rules in **one table** (a dictionary from `(current, action)` to the new status), not in a chain of `if`s: then a new rule is one new line, and a test can walk the whole table.

## Example

```python
next_status("todo", "start")      # 'doing'
next_status("doing", "finish")    # 'done'
next_status("todo", "finish")     # RuleViolation: cannot finish a task that is todo
next_status("todo", "explode")    # ValueError
```

All 12 combinations of 3 statuses and 4 actions are tested: 4 allowed, 8 refused.
