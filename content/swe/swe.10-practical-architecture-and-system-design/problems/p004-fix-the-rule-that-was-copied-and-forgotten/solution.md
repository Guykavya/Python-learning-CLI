## Approach

```python
def _check_capacity(conn, user_id):
    """Rule 3, written exactly once."""
    n = conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'", (user_id,)).fetchone()[0]
    if n >= MAX_OPEN:
        raise RuleViolation(f"assignee already has {MAX_OPEN} open tasks")

# create_task:  _check_member(...); _check_capacity(conn, assignee_id)
# update_task, assignment:
        if current_status != "done" and assignee_id != current_assignee:
            _check_capacity(conn, assignee_id)          # an open task moving to a new person
# update_task, status change:
        if current_status == "done" and current_assignee is not None:
            _check_capacity(conn, current_assignee)     # reopening makes the task open again
```

Rule 3 now has **one** definition and three callers. That is the whole fix for pain P1 of the chapter (3.1); the two failing tests of the chapter pass as a side effect of having one place for the rule. The two hidden decisions are the kind a copy-pasted rule gets wrong: a **done** task adds no load when assigned, and assigning a task to the person who **already has it** changes nothing.

## Cost

One small function and two `if`s. The three tests of chapter 3.1 found the bug only after a customer did: **write the test for the path you forgot first**, watch it fail, then fix.

## Another way

Move the rule onto the object it protects: `Task.assign(user_id, is_member, open_count)` and `Task.change_status(...)` (the domain model of chapter 8, problem p011). Then there is no `_check_capacity` to forget calling: the task refuses by itself.
