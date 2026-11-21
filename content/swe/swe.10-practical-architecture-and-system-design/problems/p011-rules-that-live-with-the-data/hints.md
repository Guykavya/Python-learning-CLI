## Hint 1

Which parts of the rules need the database? (How many open tasks has the person? Is the person a member?) The task must not ask; the caller passes the **facts** in. Everything else is a comparison on the task's own fields. Write one small helper for "the status must be X, otherwise `RuleViolation` naming both statuses", and use it in the four status methods.

## Hint 2

```text
assign: not is_member -> RuleViolation; if self.is_open and user_id != self.assignee_id and open_count >= limit -> RuleViolation; then set assignee_id
_move(expected, target): if self.status != expected: raise RuleViolation(f"cannot move from {self.status} to {target}")
start/pause/finish/reopen: call _move FIRST, then change the fields (so a refusal changes nothing)
reopen: after _move: assignee_id is not None and open_count >= limit -> RuleViolation; then status = "todo", completed_at = None
```
