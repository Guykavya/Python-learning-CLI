## Hint 1

Find the line that *touches* `task.tags` in each failing endpoint. In two of them you do not write it yourself: `response_model=TaskOut` reads `task.tags` while building the JSON, after your function has returned. Where must the tags already be by then?

## Hint 2

A loader option tells the query to fetch the relationship **now**, with an `await`: `selectinload(Task.tags)` runs one extra `SELECT ... WHERE task_id IN (...)` for all the loaded tasks. Add it with `.options(...)` on a `select`, or with `options=[...]` on `session.get`.

## Hint 3

```text
list_tasks: select(Task).options(selectinload(Task.tags)).order_by(Task.id)
get_task:   await session.get(Task, task_id, options=[selectinload(Task.tags)])
add_tag:    await session.get(Task, task_id, options=[selectinload(Task.tags)])
            then task.tags.append(Tag(name=...)); await session.commit(); return task
```
