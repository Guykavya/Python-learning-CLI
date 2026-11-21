class RuleViolation(Exception):
    pass


STATUSES = ("todo", "doing", "done")
ACTIONS = ("start", "pause", "finish", "reopen")

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
