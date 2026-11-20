# One class with SQLModel

Chapter sections 11.6 (SQLModel: one class for table and schema) and 7.2 (separate models for input, storage and output). `StaticPool` for an in-memory database is from section 11.1.

The starter uses **one** SQLModel class, `Task`, for everything: it is the table, the request body and the response. That has two problems:

1. A client can send `{"id": 99, "title": "x"}` and **choose its own id**, or overwrite the id of an existing row. The server must decide ids.
2. A `table=True` class does **not validate** when it is created, so the rules (`title` 1 to 100 characters, `priority` 1 to 5) are not enforced.

Rewrite the models with the chapter's pattern (section 11.6, `HeroBase / Hero / HeroCreate / HeroPublic`):

| Class | `table=True`? | Fields |
|---|---|---|
| `TaskBase(SQLModel)` | no | `title: str = Field(min_length=1, max_length=100)`, `priority: int = Field(default=3, ge=1, le=5)` |
| `Task(TaskBase, table=True)` | **yes** | adds `id: int \| None = Field(default=None, primary_key=True)` |
| `TaskCreate(TaskBase)` | no | nothing more: **no `id`** (the input) |
| `TaskRead(TaskBase)` | no | adds `id: int` (the output: id always present) |

Then use them in the endpoints (synchronous, with SQLModel's `Session`):

| Request | Answer |
|---|---|
| `POST /tasks` body `TaskCreate` | **201** `TaskRead`. Build the row with `Task.model_validate(data)`. |
| `GET /tasks` | list of `TaskRead`, ordered by id |
| `GET /tasks/{task_id}` | `TaskRead`, or 404 `{"detail": "Task not found"}` |

`create_app()` must give every app its **own** in-memory database: create the engine inside it with `create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)` (sync endpoints run in worker threads, and each new connection to `sqlite://` would be a different empty database, so one shared connection is needed: section 11.1 uses the same `StaticPool` trick), and create the tables with `SQLModel.metadata.create_all(engine)`.

## Example

```text
POST /tasks {"title": "write", "priority": 2}   -> 201 {"title": "write", "priority": 2, "id": 1}
POST /tasks {"id": 99, "title": "sneaky"}      -> 201 {"title": "sneaky", "priority": 3, "id": 2}    (id ignored)
POST /tasks {"title": "x", "priority": 9}      -> 422, loc ["body", "priority"], type "less_than_equal"
GET  /tasks/99                                 -> 404 {"detail": "Task not found"}
```

The tests import `create_app`, `Task`, `TaskCreate` and `TaskRead`.
