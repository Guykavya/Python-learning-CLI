## Hint 1

Search the file for the words that belong to rule 3 (`MAX_OPEN`, `status != 'done'`). Where does it appear? Now list the entry points that can give someone an open task: which of them contain that code? A rule written once and called three times cannot be forgotten in one place.

## Hint 2

```text
_check_capacity(conn, user_id): count the user's tasks with status != 'done'; if count >= MAX_OPEN raise RuleViolation(...)
create_task: after _check_member -> _check_capacity(assignee)
update_task, assignment: after _check_member, only if the task is not done AND the assignee changes -> _check_capacity(new assignee)
update_task, status change: if the task is done (a reopen) and has an assignee -> _check_capacity(current assignee), where "current" already includes the assignment of this request
```
Do the capacity check **before** the `UPDATE`, the audit line and the e-mail of that step, so a refused request leaves nothing behind.
