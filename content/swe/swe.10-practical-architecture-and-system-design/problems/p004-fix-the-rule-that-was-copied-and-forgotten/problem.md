# Fix the rule that was copied and forgotten

Chapter sections 3.1 (pain 1: a rule copied into several places, and forgotten in one) and 4.2 (the service functions). Rule 3 of Taskboard says a user may have **at most 3 open tasks** (any status except `done`). It must hold whichever way a task reaches that user:

1. a task is **created** with an assignee,
2. an existing task is **assigned** to someone (the `PATCH` use case),
3. a **done** task is **reopened** (it counts as open again).

In `solution.py` the rule is written in the first path only, so users get a 4th open task by assigning or reopening. The customer found it; the tests did not.

## Your task

Fix `solution.py` (the service functions `create_task`, `update_task` and the helper `_check_member` use a SQLite connection `conn`, as in chapter 4.2). Put the rule in **one** function, `_check_capacity(conn, user_id)`, which raises `RuleViolation(f"assignee already has {MAX_OPEN} open tasks")`, and call it from **all three paths**. Two decisions hidden in the rule are exactly what a copied rule gets wrong:

- assigning a task that is already **done** does not make the person busier (no check), and neither does assigning a task to the person who **already has it** (nothing changes);
- reopening applies the check to the task's assignee **as it is after the assignment of the same request** (a request may assign and reopen together).

Nothing else may change: the statuses move along `todo -> doing`, `doing -> todo`, `doing -> done`, `done -> todo` only; the audit lines and the e-mails stay as they are; the functions do not commit.

## Example

```python
for i in range(3):
    create_task(conn, 1, f"t{i}", 1)                # Ana now has 3 open tasks
loose = create_task(conn, 1, "loose")["id"]
update_task(conn, loose, assignee_id=1)             # today: works (a 4th task!); after the fix: RuleViolation
```

The tests try each path at the limit and also check that the people who should be allowed still are.
