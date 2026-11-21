## Approach

```python
TRANSITIONS = {
    ("todo", "start"): "doing",
    ("doing", "pause"): "todo",
    ("doing", "finish"): "done",
    ("done", "reopen"): "todo",
}


def next_status(current, action):
    if current not in STATUSES:
        raise ValueError(f"unknown status {current!r}")
    if action not in ACTIONS:
        raise ValueError(f"unknown action {action!r}")
    try:
        return TRANSITIONS[(current, action)]
    except KeyError:
        raise RuleViolation(f"cannot {action} a task that is {current}") from None
```

A **table** beats a chain of `if`s: the rules are readable at a glance, a new rule is one new line, and the test can walk **every** pair (3 x 4 = 12) instead of sampling a few. This is exactly the shape the chapter's `ALLOWED` set has (`{("todo", "doing"), ...}`), with the action added so that the message can say what was attempted.

## Complexity

O(1) per call.

## Another way

An `enum.Enum` for statuses and actions prevents typos at import time. A library such as `transitions` (not installed here) builds state machines with callbacks; for four moves a dictionary is enough, and the chapter's advice stands: do not add machinery before the pain.
