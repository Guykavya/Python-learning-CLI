## Hint 1

Work in the order of section 22 and let the first failing test tell you what is next. Almost every test starts with the `signup` fixture (register + login), so build `get_session`, `get_settings` and the two `/auth` routes first, and include their router in `create_app`. Then `current_user`, `POST /teams` and `team_member`/`team_owner`, then the tasks router, then the WebSocket, and the error envelope last (the earlier tests compare status codes, the later ones also the envelope).

## Hint 2

Reuse what you wrote earlier in this module: the envelope (section 8.2), the dependency stack `current_user` → `team_member` → `team_owner` (problems 34 and 35), `exclude_unset` for PATCH (section 7.5), pagination with `limit`/`offset` and a `count()` query (section 11), the `ConnectionManager` (problem 40) and the WebSocket check before `accept()` (problem 41), routers (problem 43). Section 22 gives the code of every router; the differences here are the extra `GET` of one task and the envelope.

## Hint 3

```text
deps:     get_session(request) yields a session from request.app.state.sessionmaker
          current_user(token=Depends(oauth2_scheme), session, settings) -> User or 401 (+ WWW-Authenticate)
          team_member(team_id, user, session) -> Membership or 404;  team_owner(member) -> 403 unless role == "owner"
tasks:    load_task(session, team_id, task_id): select Task where id == task_id AND team_id == team_id, else 404
          after commit: out = TaskOut.model_validate(task); broadcast {"event": "task.created", "task": out.model_dump(mode="json")}
ws:       open a short session, user_from_token + find_membership, close(code=1008) if not allowed, else manager.connect
errors:   app.add_exception_handler(starlette HTTPException, handler) -> envelope(status, ERROR_CODES.get(...), str(detail), headers=exc.headers)
          app.add_exception_handler(RequestValidationError, handler) -> 422 + details [{"loc": list(e["loc"]), "type": e["type"], "msg": e["msg"]}]
create_app: add both handlers, include auth, teams, tasks, ws routers
```
