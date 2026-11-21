# Rules that live with the data

Chapter sections 8.1 to 8.3 (the domain model: rules live with the data they protect) and 8.5 (rules tested with no set-up at all). In the service layer, the rules about a **task** (status moves, who may be assigned, what reopening needs) are scattered next to storage calls, so you cannot test them without a unit of work. A **domain model** puts the rules into the object. `Task` stops being a bag of fields and gains **behaviour**: methods that change its state and **refuse** changes that break a rule.

A domain object must not call the database. The facts it needs (is this person a member? how many open tasks do they have?) are **passed in as plain arguments** by the caller. That keeps the domain code pure: ordinary Python, no I/O, trivially testable.

## What to write

`Task` (a dataclass) and the errors are given. Add these methods to `Task`. All of them raise `RuleViolation` when a rule is broken and **leave the task unchanged** in that case:

```python
def assign(self, user_id, *, is_member, open_count, limit=3): ...
def start(self): ...               # todo  -> doing
def pause(self): ...               # doing -> todo
def finish(self, now): ...         # doing -> done; sets completed_at = now
def reopen(self, open_count, limit=3): ...   # done  -> todo; clears completed_at
```

The rules (the work-in-progress limit is `limit`, 3 by default):

- `assign`: if `is_member` is false -> `RuleViolation("assignee is not a member of this project")`. If the task is **open** (status is not `done`), the person is **not already its assignee**, and `open_count >= limit` -> `RuleViolation(f"assignee already has {limit} open tasks")`. Otherwise set `assignee_id = user_id`. (A done task adds no load, and assigning a task to the person who already has it changes nothing, so neither needs a free slot.)
- `start`, `pause`, `finish`, `reopen`: the status must be the one named above, else `RuleViolation(f"cannot move from {self.status} to {target}")` where `target` is the status the method would set.
- `reopen`: if the task has an assignee and `open_count >= limit` -> `RuleViolation(f"assignee already has {limit} open tasks")` (the reopened task counts as open again; `open_count` is the assignee's **current** number of open tasks). The status check comes **first**.

## Example

```python
t = Task(1, 1, "Write docs", "todo", None, "2026-01-01T00:00:00")
t.assign(1, is_member=True, open_count=2)        # fine: assignee_id == 1
t.assign(2, is_member=True, open_count=3)        # RuleViolation: assignee already has 3 open tasks
t.start(); t.finish("2026-02-02T00:00:00")       # status 'done', completed_at set
t.reopen(open_count=3)                           # RuleViolation: the assignee is full
```

The tests build a `Task` directly and call a method: no database, no fake, no fixture.
