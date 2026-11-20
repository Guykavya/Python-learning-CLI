# Only your own tasks

Chapter section 12.4 (ownership checks: load the row in a dependency, 404 if absent or not yours), with 12.3 for `get_current_user` and 9.3 for sub-dependencies. Status codes are from p019.

Two users share one task API. Logging in works (the starter gives a simplified `get_current_user` that accepts the fixed tokens `tok-asha` and `tok-ben`; p034 built the real one). What is missing is **authorisation**: today any logged-in user could read, change or delete any task just by changing the number in the URL. That bug has a name, **IDOR** (insecure direct object reference), and it is one of the most common API flaws.

Write `create_app()` with its own task store (a dict `id -> {"id", "title", "done", "owner"}`, ids from 1 in order of creation across all users, never reused after a delete: `itertools.count(1)` is handy) and these endpoints, **all requiring a logged-in user**:

| Request | Answer |
|---|---|
| `GET /tasks` | 200, **only the caller's** tasks, ordered by id |
| `POST /tasks` body `{"title": ...}` (1+ characters) | 201 `{"id", "title", "done": false, "owner": <caller>}` |
| `GET /tasks/{task_id}` | 200 the task |
| `PATCH /tasks/{task_id}` body `{"done": true/false}` | 200 the updated task |
| `DELETE /tasks/{task_id}` | 204, empty body |

The rules:

- **The owner is always the caller.** The body model has only `title`; an `"owner"` key in the body is ignored.
- **A task that belongs to someone else is answered exactly like a task that does not exist**: 404 `{"detail": "Task not found"}`. Section 12.4 explains the choice: a 403 would confirm that task 1 exists.
- Write the check **once**, as a dependency `get_own_task(task_id, user)` that loads the task and raises the 404; the three single-task endpoints depend on it.
- No token or a bad token: 401 (from `get_current_user`, already done).

## Example

```text
asha: POST /tasks {"title": "pay rent"}          -> 201 {"id": 1, "title": "pay rent", "done": false, "owner": "asha"}
asha: POST /tasks {"title": "gym", "owner": "ben"} -> 201 {"id": 2, "title": "gym", "done": false, "owner": "asha"}
ben:  POST /tasks {"title": "call mum"}          -> 201 {"id": 3, ..., "owner": "ben"}
ben:  GET /tasks                                 -> 200 [{"id": 3, "title": "call mum", "done": false, "owner": "ben"}]
ben:  GET /tasks/1                               -> 404 {"detail": "Task not found"}
ben:  DELETE /tasks/1                            -> 404 {"detail": "Task not found"}   (task 1 is still there)
asha: PATCH /tasks/1 {"done": true}              -> 200 {"id": 1, "title": "pay rent", "done": true, "owner": "asha"}
```

Requests carry `Authorization: Bearer tok-asha` or `Bearer tok-ben`. The tests import `create_app` and build a new app for every test.
