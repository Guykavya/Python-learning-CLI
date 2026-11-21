class RuleViolation(Exception):
    pass


STATUSES = ("todo", "doing", "done")
ACTIONS = ("start", "pause", "finish", "reopen")


def next_status(current, action):
    # TODO: one table of allowed moves; RuleViolation naming both for the others; ValueError for unknown words
    return current
