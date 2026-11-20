# A task-management API

The project of the module (chapter section 22, steps 1 to 8): **TaskFlow**. Users register and log in; users create **teams**; the team owner adds members; members create, read, update and delete **tasks** inside their team; everyone connected to a team receives **real-time events** over a WebSocket. Everything in one file, `solution.py`, with an app factory `create_app(settings)`.

The starter already contains the parts that are pure typing work, exactly as in the chapter: `Settings` (with `from_env()`, section 18), `make_engine` (in-memory SQLite shares one connection with `StaticPool`, section 11), the tables `User`, `Team`, `Membership`, `Task`, the schemas (`UserCreate`, `UserOut`, `LoginIn`, `TokenOut`, `TeamCreate`, `TeamOut`, `MemberAdd`, `TaskCreate`, `TaskPatch`, `TaskOut`, `TaskPage`, `Status`), the security helpers (`hash_password`, `verify_password`, `create_token`, `decode_token`), `ConnectionManager` and `team_room(team_id)`, and a `create_app` whose lifespan creates the tables and puts `settings`, `sessionmaker` and `manager` on `app.state`. The chapter splits these into `app/config.py`, `app/models.py` and so on; here they live in one file because the runner copies only `solution.py`.

## What you build

**Dependencies** (section 22, step 4): `get_session` (one `AsyncSession` per request from `request.app.state.sessionmaker`), `get_settings`, `get_manager`, `OAuth2PasswordBearer(tokenUrl="/auth/login")`, `current_user` (401 with `WWW-Authenticate: Bearer` for a missing, bad or expired token), `team_member` (**404** `Team not found` when the user is not a member), `team_owner` (**403** for a plain member).

**Routes:**

| Route | Behaviour |
|---|---|
| `POST /auth/register` | `UserCreate` → **201** `UserOut` (`id`, `email`, `name`; never the hash). Email stored lower-case. Same email again → **409**. |
| `POST /auth/login` | JSON `LoginIn` → `{"access_token": <JWT>, "token_type": "bearer"}`; email matched case-insensitively; wrong email or password → **401**. |
| `GET /health` | `{"status": "ok"}` (given). |
| `POST /teams` | creates the team **and** the creator's `Membership` with role `owner`, in one transaction → **201** `TeamOut`. |
| `GET /teams` | the teams the user belongs to, by id. |
| `POST /teams/{team_id}/members` | owner only; body `{"email": ...}`; unknown email → 404; already a member → 409; → **201** `UserOut`. |
| `POST /teams/{team_id}/tasks` | member; `TaskCreate`; `assignee_id` must be a member of the team (else **422**) → **201** `TaskOut` (status `todo`, `creator_id` = the user). |
| `GET /teams/{team_id}/tasks` | member; `?status=`, `limit` (1 to 100, default 20), `offset` (≥ 0) → `{"items": [...], "total": N}` ordered by id. |
| `GET /teams/{team_id}/tasks/{task_id}` | member → `TaskOut`. |
| `PATCH /teams/{team_id}/tasks/{task_id}` | member; changes **only** the fields sent (`exclude_unset=True`) → `TaskOut`. |
| `DELETE /teams/{team_id}/tasks/{task_id}` | the team owner or the task's creator (else **403**) → **204**. |
| WebSocket `/ws/teams/{team_id}?token=...` | check the token **and** the membership **before** `accept()`; refuse with close code **1008**. Then keep the socket in the room `team_room(team_id)`. |

**Rules that the tests enforce** (the business spec of section 22):

- A team is invisible to non-members: **every** team route answers **404** to an outsider, not 403.
- A task is looked up **inside the team of the URL** (`Task.id == task_id` and `Task.team_id == team_id`), so a task id from another team is a 404.
- Create, update and delete broadcast to the team's room: `{"event": "task.created", "task": <TaskOut as JSON>}`, `{"event": "task.updated", "task": ...}`, `{"event": "task.deleted", "task_id": ID}`. The event's `task` equals the HTTP response body.
- **One error envelope** for every error (section 8.2), registered for **Starlette's** `HTTPException` (so the router's own 404 is covered) and for `RequestValidationError`:

  ```text
  {"error": {"code": "not_found", "message": "Task not found"}}
  {"error": {"code": "validation_failed", "message": "Request data is invalid",
             "details": [{"loc": ["body", "title"], "type": "missing", "msg": "Field required"}]}}
  ```

  Codes: 400 `bad_request`, 401 `unauthorized`, 403 `forbidden`, 404 `not_found`, 405 `method_not_allowed`, 409 `conflict`, 422 `validation_failed`, anything else `http_error`. Validation errors keep status **422**. Keep the exception's `headers` (the `WWW-Authenticate` of a 401).
- `create_app()` with no settings reads the environment and must fail at start-up when `APP_SECRET_KEY` is missing (the starter's `Settings.from_env` already does this).
- `/openapi.json` lists every HTTP route above.

## Example

```text
POST /auth/register {"email": "Asha@Example.com", "name": "Asha", "password": "password123"}
  -> 201 {"id": 1, "email": "asha@example.com", "name": "Asha"}
POST /auth/login {"email": "asha@example.com", "password": "password123"}
  -> 200 {"access_token": "eyJ...", "token_type": "bearer"}
POST /teams {"name": "Core"}   (Authorization: Bearer eyJ...)        -> 201 {"id": 1, "name": "Core"}
POST /teams/1/tasks {"title": "ship"}                                -> 201 {"id": 1, "title": "ship", "status": "todo", ...}
   ...and every socket on /ws/teams/1 receives {"event": "task.created", "task": {...same...}}
GET  /teams/1/tasks   by someone outside the team                    -> 404 {"error": {"code": "not_found", ...}}
GET  /teams/1/tasks?limit=0                                          -> 422 {"error": {"code": "validation_failed", "details": [{"loc": ["query", "limit"], "type": "greater_than_equal", ...}]}}
```

## How to work

Follow the steps of section 22 and run the tests after each one: dependencies, auth routes, teams, tasks, the WebSocket route, then the error envelope. The tests are in `test_solution.py`: read them like a specification. Each test builds a **fresh app with a fresh in-memory database**, so tests never see each other's data. The whole file runs in about 6 to 10 seconds (most of it is the deliberately slow password hashing).
