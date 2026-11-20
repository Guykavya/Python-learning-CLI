# Problem plan: swe.05 FastAPI (50 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `swe.05.p001`…`p050`.

**Mix:** 18 drill, 19 applied, 9 deep, 4 challenge. **Kinds:** 37 code, 9 trace, 4 explain.
**assessment:** explain = p016, trace = p015, fix = p017, build = p050.
**★ core set:** p003, p004, p006, p011, p015, p016, p017, p018, p020, p022, p024, p025, p029, p031, p033, p034, p035, p040, p047, p050 (outcomes: a validated, documented, tested API from an empty folder; where validation happens and what a 422 means).

**Testing notes**
- `solution.py` defines `app` (or `create_app(settings)` from p021 on). Tests use `with TestClient(app) as client:` (the `with` runs the lifespan). `httpx2` is installed so Starlette shows no deprecation warning.
- Replace dependencies with `app.dependency_overrides[get_db] = ...` (Ch. 9.6) and clear them in a fixture `finally`.
- **SQLite and threads:** TestClient runs sync endpoints in a thread pool, so an in-memory database needs `create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)`; otherwise use a file in `tmp_path`. Async problems use `sqlite+aiosqlite:///` on a `tmp_path` file.
- Async timing problems (p027, p028) run `httpx.AsyncClient(transport=httpx.ASGITransport(app=app))` with `asyncio.gather` inside `asyncio.run`; sleeps of 0.3 s, thresholds with wide margins (concurrent < 0.6 s, serial ≥ 0.85 s).
- 422 problems compare `detail[i]["loc"]` and `detail[i]["type"]` only (Pydantic v2 error types like `missing`, `int_parsing`, `greater_than_equal` are stable); never the human `msg` text.
- Unhandled errors: `TestClient(app, raise_server_exceptions=False)` to see the 500 the user would get.
- WebSockets: `client.websocket_connect("/ws/...")`. JWT: `pyjwt` with a fixed key and an injected clock for expiry.
- Import cost: FastAPI + TestClient ~0.6 s; SQLModel/SQLAlchemy add ~0.5 s.

## A. ASGI (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | A hand-written ASGI app ✅ | drill | code | `async def app(scope, receive, send)` (Ch. 1.2): `/hello` → 200 JSON, else 404; the test drives it in-process with fake `receive`/`send` and checks the `http.response.start` and `http.response.body` messages |
| 2 | ASGI versus WSGI ✅ | drill | explain | why one WSGI worker handles one request at a time, what an event loop adds, why WebSockets need ASGI; checklist from Ch. 1.1 |

## B. Parameters (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 3 | Where does each parameter come from? ✅ | drill | trace | `⚠ HAND-TRACE` the chapter's `user_posts(user_id: int, limit: int = 10, draft: bool = False, tag: str | None = None)`; 8 URLs (`draft=yes`, `draft=0`, `limit=abc`, missing id…); write the status and the returned dict or the 422 `loc` |
| 4 | Constrain the parameters ✅ | drill | code | `Annotated[int, Path(ge=1)]`, `Query(max_length=30, pattern=...)`, a list query `?tag=a&tag=b`; the test checks good calls and that each bad one is a 422 at the right `loc` |
| 5 | Headers and cookies ✅ | drill | code | `user_agent: Annotated[str | None, Header()]` (underscore → hyphen), `X-Request-ID` header, a `session` cookie; missing optional ones give `None` |

## C. Bodies and Pydantic v2 (Ch. 4–5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | A task body ✅ | drill | code | `TaskIn(title: str, priority: int = 3, tags: list[str] = [])`; `POST /tasks` returns 201 with an id; body sent as form data or as a list → 422 |
| 7 | Several body parts ✅ | applied | trace | `⚠ HAND-TRACE` endpoints with one model, two models, a model + `Body(embed=True)`, a model + a single `Body()` int (Ch. 4.2); write the JSON shape each expects |
| 8 | Field constraints and aliases ✅ | drill | code | `Field(min_length=, gt=, alias="userName")`, `populate_by_name`; checks both names and the 422 for each constraint |
| 9 | Lax or strict? ✅ | drill | trace | `⚠ HAND-TRACE` `Lax(n: int, ok: bool)` and `Strict` with `strict=True` (Ch. 5.4); for inputs `"5"`, `5.0`, `5.5`, `"true"`, `"yes"`, `1`, write the stored value or `error` |
| 10 | Field validators ✅ | applied | code | `@field_validator`: strip and lower-case the email, reject disposable domains from a list, title-case the name; `mode="before"` for a comma string → list |
| 11 | Rules across fields ✅ | applied | code | `Booking(start, end, guests, room)` with `@model_validator(mode="after")`: end after start, max 4 guests for `"double"`; the 422 `loc` is the model root (`["body"]`) |
| 12 | Discriminated unions ✅ | deep | code | `Payment = Annotated[Card | Bank | Upi, Field(discriminator="method")]`; each method's fields validated; an unknown method gives one clear error, not three (Ch. 5.9) |
| 13 | Computed fields and output names ✅ | applied | code | `@computed_field` `total_paise`, `serialization_alias="createdAt"`, `model_dump(by_alias=True, exclude_none=True)` |
| 14 | Models from ORM objects ✅ | drill | code | `model_config = ConfigDict(from_attributes=True)`; `UserOut.model_validate(fake_orm_user)`; extra attributes (the hash) are not copied |

## D. Where validation happens: the 422 (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | Read a 422 ✅ | deep | trace | `assessment = "trace"`. `⚠ HAND-TRACE` 5 bad requests to the chapter's `POST /projects/{project_id}/tasks` (Ch. 6.2): bad path id, missing body field, wrong type in a nested list, bad query, invalid JSON; write each `detail` item as `loc` + `type`, in order |
| 16 | Where does validation happen? ✅ | applied | explain | `assessment = "explain"`. Outcome 2. Type hints describe, Pydantic enforces at the edge; what a 422 means and what it is **not** (not a server bug, not a business rule failure like "title taken" = 409); request lifecycle (Ch. 6.1, 6.3) |

## E. Responses (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | Fix the leaky response ✅ | applied | code | `assessment = "fix"`. Registering returns the stored user **with its password hash**; fix with `response_model=UserOut` (Ch. 7.2, "Try it: the leaky response"); tests check no `password`/`hash` key at any depth and the 201 status |
| 18 | `PATCH` only what was sent ✅ | applied | code | `TaskPatch` with all-optional fields; `model_dump(exclude_unset=True)`; sending `{"due": null}` clears the date but omitting `due` keeps it |
| 19 | Status codes and `Location` ✅ | drill | code | create → 201 with `Location`, delete → 204 with an empty body, conflict → 409 via `HTTPException` |

## F. Errors (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | One error shape for the whole API ✅ | applied | code | handlers for `HTTPException`, `RequestValidationError` and a domain `NotFound` that all return `{"error": {"code", "message", "details"}}` (Ch. 8.2); 422 details keep `loc` |
| 21 | A 500 that tells nothing ✅ | deep | code | a catch-all handler logs the traceback with a request id and returns a generic 500 envelope containing only that id; tested with `raise_server_exceptions=False` and `caplog` |

## G. Dependency injection (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 22 | A pagination dependency ✅ | drill | code | `Pagination = Annotated[Page, Depends(page_params)]` reused by 3 endpoints; `limit` 1..100, `offset ≥ 0`; one source of truth |
| 23 | Count the calls ✅ | applied | trace | `⚠ HAND-TRACE` a dependency tree where `get_db` is used by two sub-dependencies and the endpoint (Ch. 9.3, "Try it: count the calls"); write how many times each runs per request, then with `use_cache=False` |
| 24 | Setup and cleanup with `yield` ✅ | applied | code | `get_session()` yields a session, commits on success, rolls back on an exception, always closes; the test's fake session records the calls for a good and a failing request |
| 25 | Make it testable with overrides ✅ | applied | code | refactor an endpoint that reads the clock and settings directly into `Depends(get_clock)`, `Depends(get_settings)`; tests override both and check "overdue" logic |
| 26 | A class dependency with state ✅ | deep | code | `RateLimit(limit, window)` instance used as `Depends(RateLimit(3, 60))`, keyed by API key, fake clock override; 4th call → 429 with `Retry-After` |

## H. Async and async databases (Ch. 10–11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | Who blocks the event loop? ✅ | deep | trace | `⚠ HAND-TRACE` three endpoints: `async def` with `time.sleep(0.3)`, `def` with `time.sleep(0.3)`, `async def` with `await asyncio.sleep(0.3)`; three concurrent calls to each; write which finish together and which one at a time (Ch. 10.2), not the exact times |
| 28 | Move blocking work off the loop ✅ | applied | code | an `async def` endpoint must call a blocking `make_report()` via `asyncio.to_thread`; three concurrent requests finish in < 0.6 s; result unchanged |
| 29 | An async database with a lifespan ✅ | challenge | code | engine created in `lifespan`, `AsyncSession` dependency, `GET/POST /tasks`; tests run the app twice (fresh database each time) |
| 30 | The `MissingGreenlet` trap ✅ | deep | code | a response that touches a lazy relationship after the query raises `MissingGreenlet`; fix with `selectinload` in the query (Ch. 11.5); the test checks the JSON includes the tags |
| 31 | One class with SQLModel ✅ | applied | code | `Task(SQLModel, table=True)` plus `TaskCreate`/`TaskRead`; the id is never accepted from the client (Ch. 11.6) |

## I. Authentication and authorisation (Ch. 12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 32 | Password hashing with the standard library ✅ | drill | code | `hash_password` with `hashlib.pbkdf2_hmac`, random salt, iterations stored in the string; `verify` with `hmac.compare_digest`; the same password twice → different strings |
| 33 | Tokens with JWT ✅ | applied | code | `make_token(user_id, now)`/`read_token(token, now)` with `pyjwt`: `sub`, `exp`; expired, wrong key, `alg: none` and a tampered payload each raise `InvalidToken` |
| 34 | `get_current_user` ✅ | applied | code | `OAuth2PasswordBearer(tokenUrl="token")`, `POST /token` with form data, `GET /me`; missing/bad token → 401 with `WWW-Authenticate: Bearer` |
| 35 | Only your own tasks ✅ | applied | code | two users; reading or editing another user's task returns 404 (do not reveal it exists); listing shows only own tasks (Ch. 12.4) |

## J. Middleware, CORS, background tasks (Ch. 13–14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 36 | Request id and timing middleware ✅ | drill | code | `@app.middleware("http")` adds `X-Request-ID` (reuses a valid incoming one) and `Server-Timing`; works for 404s too |
| 37 | What will CORS allow? ✅ | deep | trace | `⚠ HAND-TRACE` `CORSMiddleware(allow_origins=[...], allow_credentials=True, allow_methods=["GET","POST"])`; 5 preflight/simple requests from different origins and methods; write status and `Access-Control-Allow-Origin` (or none); confirm by running when writing the answer |
| 38 | A background task after the response ✅ | drill | code | `BackgroundTasks.add_task(send_welcome, email)`; the response is returned first; the test's fake outbox has one message after the request; failures in the task do not change the response status |

## K. WebSockets and uploads (Ch. 15–16)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 39 | A WebSocket echo ✅ | drill | code | `/ws/echo` echoes text upper-cased, `"bye"` closes with code 1000 |
| 40 | Broadcast to a room ✅ | challenge | code | `ConnectionManager` with rooms (Ch. 15.3): join, broadcast to the room only, remove on `WebSocketDisconnect`; tests open 3 sockets in 2 rooms |
| 41 | Authenticate a WebSocket ✅ | applied | code | token as a query parameter; bad token → close with code 1008 before accepting messages; messages over 4 KB → close 1009 |
| 42 | Safe uploads ✅ | applied | code | `UploadFile`: only `text/csv`, max 1 MB read in chunks (not `.read()` of everything), returns row count; too big → 413 |

## L. Structure, settings and docs (Ch. 17–19)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 43 | Split into routers ✅ | drill | code | `APIRouter(prefix="/tasks", tags=["tasks"], dependencies=[Depends(require_user)])`; `app.include_router`; the dependency applies to all routes in the router |
| 44 | Settings from the environment ✅ | drill | code | the chapter's `Settings(BaseModel)` filled from `os.environ` (Ch. 18) (`DATABASE_URL`, `SECRET_KEY` required, `DEBUG` bool); missing secret fails at start-up with a clear error; tests use `monkeypatch.setenv` |
| 45 | Read the OpenAPI schema ✅ | drill | trace | `⚠ HAND-TRACE` given a 3-endpoint app, write the paths, methods, required parameters and response status codes that `app.openapi()` lists (Ch. 19.1); confirm by running when writing the answer |
| 46 | Flask, FastAPI or Django? ✅ | deep | explain | three project briefs (admin-heavy inventory, real-time task API, a small internal form tool); choose and defend with Ch. 23's table; checklist: async needs, admin, team skills, validation, ecosystem |

## M. Testing (Ch. 20)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 47 | Validation tests that catch mutants ✅ | challenge | code | the learner writes `CASES = [(payload, expected_status), ...]` for `POST /tasks`; the test runs them against the correct app (all must match) and against 4 mutants (each loosened rule must be caught by at least one case) |
| 48 | `async def` or `def`? ✅ | applied | explain | for 5 endpoint bodies (pure computation, `requests.get`, `await client.get`, SQLAlchemy sync session, file read) choose and explain (Ch. 10.3); checklist |
| 49 | The life of one request ✅ | deep | trace | `⚠ HAND-TRACE` middleware, dependency with `yield`, endpoint, background task each append to a list; write the order for a successful request and for one where the endpoint raises `HTTPException` |

## N. Project (Ch. 22)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 50 | A task-management API ✅ | challenge | code | `assessment = "build"`. `create_app(settings)`: users (register, token), teams (create, add member), tasks per team (CRUD, PATCH, pagination), only team members see a team's tasks, one error envelope, WebSocket `/ws/teams/{id}` that receives `task_created` events. Tests: full flow, outsider gets 404, 422 shapes, WebSocket event after a POST, OpenAPI lists every route |

## Counts check

Tiers: drill 1, 2, 3, 4, 5, 6, 8, 9, 14, 19, 22, 32, 36, 38, 39, 43, 44, 45 (18); applied 7, 10, 11, 13, 16, 17, 18, 20, 23, 24, 25, 28, 31, 33, 34, 35, 41, 42, 48 (19); deep 12, 15, 21, 26, 27, 30, 37, 46, 49 (9); challenge 29, 40, 47, 50 (4). Total 50.
Kinds: trace 3, 7, 9, 15, 23, 27, 37, 45, 49 (9); explain 2, 16, 46, 48 (4); code 37.

## Risks and open questions

- FastAPI/Pydantic change details between versions (e.g. the 422 `input` field, OpenAPI 3.1 shapes). Traces p015 and p045 are confirmed by running when written; pin the versions used in `solution.md`.
- p027/p028 depend on timing; keep margins wide and the sleeps short. If they prove flaky on Windows, turn p028 into "the order of completion" instead of a time threshold.
- p044 uses the chapter's hand-written `Settings(BaseModel)` read from `os.environ` (Ch. 18); `pydantic-settings` is not installed, so do not use `BaseSettings`.
