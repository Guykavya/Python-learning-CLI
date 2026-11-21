## Hint 1

Write the interface from the point of view of the **caller**: what does a rule ask? ("how many open tasks does Ana have?", "give me task 7", "store my changes"). Each question becomes one method. Which method needs a function that turns a `sqlite3.Row` into a `Task`?

## Hint 2

```text
_task(row): Task(id=row["id"], ... completed_at=row["completed_at"])
add: INSERT ... ; task.id = cursor.lastrowid; return task
get: SELECT * WHERE id; no row -> raise NotFound(f"task {id} not found"); return _task(row)
save: UPDATE tasks SET title, status, assignee_id, completed_at WHERE id
open_count_for: SELECT COUNT(*) WHERE assignee_id = ? AND status != 'done'
list_for_project: SELECT * WHERE project_id = ? [AND status = ?] ORDER BY id
```
Never call `commit()` in these methods.
