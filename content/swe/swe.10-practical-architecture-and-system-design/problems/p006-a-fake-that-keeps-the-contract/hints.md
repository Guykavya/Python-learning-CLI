## Hint 1

Read the contract tests as the specification: they say what any repository must do. Which behaviour of a **real database** would a "lazy" dictionary of objects not have? Think about what happens when you change an object you were handed, and do not call `save`.

## Hint 2

```text
add:   task.id = next_id; next_id += 1; store copy.copy(task); return task
get:   missing -> NotFound(f"task {id} not found"); return copy.copy(stored)
save:  store copy.copy(task)
open_count_for / list_for_project: filter the stored tasks (list: sorted by id), return COPIES
```
