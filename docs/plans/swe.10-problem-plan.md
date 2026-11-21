# Problem plan: swe.10 Practical architecture and system design (25 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `swe.10.p001`…`p025`.

**Mix:** 6 drill, 11 applied, 6 deep, 2 challenge. **Kinds:** 17 code, 5 trace, 3 explain.
**assessment:** explain = p008, trace = p010, fix = p004, build = p025.
**★ core set:** p002, p004, p005, p006, p008, p009, p010, p013, p019, p022, p024, p025 (outcomes: explain the concrete pain a repository layer removes; sketch a system design and discuss trade-offs).

**Testing notes**
- Problems use the chapter's running example **Taskboard** (Ch. 2): projects, members, tasks with a WIP limit, an e-mail on assignment, statuses `todo → doing → done`. The schema, the domain errors (`DomainError`, `NotFound`, `InvalidInput`, `RuleViolation`, Ch. 4.2) and a `FakeMailer` go into `conftest.py`.
- SQLite in `tmp_path` (or `:memory:` when one connection is enough); HTTP-level problems use FastAPI `TestClient` with the chapter's safety-net tests (Ch. 2.3) as the regression suite.
- **Contract tests** (p006, p007) are one list of check functions run against both the SQLite repository and the fake (Ch. 6.3), parametrised with `pytest.mark.parametrize`.
- Design problems are numeric or structural (estimates, hashing, fan-out costs) so they can be tested; the open-ended "draw the design" part is in explain answers and in the project's ADR, which the test checks only for structure (sections present), not content.

## A. Pain first (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Pain or style? ✅ | drill | trace | `⚠ HAND-TRACE` 8 complaints about a codebase ("routes are long", "the WIP rule exists in three places", "tests need a running server", "we might switch databases one day", …); write `pain` or `style` and the remedy from the ladder (Ch. 1.4, "Try it: pain or style?") |
| 2 | Extract the service layer ✅ | applied | code | move the create-task logic out of the route into `create_task(conn, project_id, title, assignee_id)` raising domain errors; the route only translates (Ch. 4.2–4.3); the HTTP safety-net tests still pass and a direct call of the service works without FastAPI |
| 3 | Domain errors to HTTP, in one place ✅ | drill | code | `domain_error_to_http(exc)` → `(status, body)`: `NotFound` 404, `InvalidInput` 422, `RuleViolation` 409, anything else re-raised; one exception handler registered for `DomainError` |
| 4 | Fix the rule that was copied and forgotten ✅ | applied | code | `assessment = "fix"`. The WIP limit is checked on create but not when a task is reassigned by `PATCH` or reopened from `done` (Ch. 3.1, pain 1). Put the check in one service function used by all three paths; tests try each path at the limit |

## B. The repository (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | A repository in business words ✅ | applied | code | `SqliteTaskRepo(conn)` with `add`, `get` (returns a `Task` dataclass or raises `NotFound`), `open_count_for(user_id)`, `list_for_project(project_id, status=None)`; no SQL outside the repository; services take `repos` (Ch. 5.2–5.3) |
| 6 | A fake that keeps the contract ✅ | applied | code | `FakeTaskRepo` in memory; the given contract tests (ordering, `NotFound`, counting only open tasks, ids increasing) run against the SQLite repository and the fake, and both must pass (Ch. 6.1, 6.3) |
| 7 | Contract tests that catch a lying fake ✅ | deep | code | the learner writes the contract checks for `ProjectRepo.add_member`/`is_member`; the test runs them against the real repository (must pass) and two lying fakes (duplicate members allowed; membership case-sensitive) that must each be caught |
| 8 | What did the repository buy you? ✅ | applied | explain | `assessment = "explain"`. Outcome 1. Using the pain log of Ch. 3.4, name the concrete pains the repository removed (rules tested without a database in milliseconds, one place for SQL, business words) and what it did **not** buy (switching databases is rarely real; it adds code); when a one-table app should skip it (Ch. 6.4, "Try it: the repository for a one-table app") |

## C. Unit of work (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | A SQLite unit of work ✅ | applied | code | `SqliteUnitOfWork(path)` as a context manager exposing repositories; nothing is saved unless `uow.commit()` is called; an exception or leaving without commit rolls back; a second `with` sees committed data only (Ch. 7.2) |
| 10 | Where does the commit belong? ✅ | applied | trace | `assessment = "trace"`. `⚠ HAND-TRACE` five versions of "assign task, then send e-mail" with the commit in different places and the mailer failing; write for each whether the task is saved, whether the e-mail went out, and whether the database is half-saved (Ch. 7.1, 7.3, "Try it: where does the commit belong?") |

## D. The domain model (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 11 | Rules that live with the data ✅ | drill | code | `Task.assign(user_id, is_member, open_count, limit)`, `start()`, `finish()`, `reopen(open_count, limit)` raising `RuleViolation`; tested with **no set-up at all**, plain objects (Ch. 8.3, 8.5) |
| 12 | The status flow ✅ | drill | code | `next_status(current, action)` from a transitions table: `start` todo→doing, `finish` doing→done, `reopen` done→todo, anything else `RuleViolation` naming both; all 9 pairs tested |

## E. Events and the outbox (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 13 | Events and an outbox ✅ | challenge | code | the service records `TaskAssigned` on the task; the unit of work saves the task **and** the outbox row in one transaction; `dispatch(uow, handlers)` delivers unsent events and marks them; a failing mailer leaves the event unsent for the next run, never a half-saved task (Ch. 9.3–9.6) |
| 14 | Two dispatchers at once ✅ | deep | trace | `⚠ HAND-TRACE` two dispatchers read the outbox in an interleaved order without claiming rows; write how many e-mails each user gets, then with a claim (`UPDATE ... WHERE claimed_by IS NULL`) (Ch. "Try it: what if two dispatchers run at once?") |

## F. The shape and its bill (Ch. 10–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | Check the dependency rule ✅ | deep | code | `violations(sources: dict[module, source_text], layers)` uses `ast` to find imports; the domain may import nothing from services/adapters/web, services nothing from web; reports `(module, imported)` pairs (Ch. 10.2, "Try it: draw the line") |
| 16 | Monolith or services? ✅ | deep | explain | three teams/products (Ch. "Try it: monolith or services?"); choose monolith, modular monolith or services and defend with the availability tax and the reasons to split (Ch. 11.3–11.5); checklist |
| 17 | Spot the retry storm ✅ | drill | trace | `⚠ HAND-TRACE` a request passing three services, each retrying 3 times; write the worst-case calls reaching the database, then with retries only at the edge, then with a timeout budget (Ch. 12.2, "Try it: spot the retry storm") |
| 18 | Degrade gracefully ✅ | applied | code | `recommendations(user, primary, cache, breaker, clock)`: call the primary with a timeout; on failure or open breaker serve the last cached list marked `stale=True`; with no cache, a fixed popular list; never raise to the page (Ch. 12.3–12.4) |

## G. System design (Ch. 13–17)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | Back-of-the-envelope estimates ✅ | drill | code | `estimate(dau, writes_per_user, reads_per_write, bytes_per_item, years, peak_factor)` → average and peak QPS for reads and writes, storage in GB; rounding stated (Ch. 13.3, "Try it: size a small product") |
| 20 | Fan-out on write or on read? ✅ | applied | trace | `⚠ HAND-TRACE` a feed with given followers per user and posting/reading rates; write the writes per second for fan-out on write, the reads per second for fan-out on read, and the hybrid rule for a celebrity account (Ch. 17.2) |
| 21 | Why are the servers uneven? ✅ | applied | code | simulate round-robin and least-connections over requests with given durations; return per-server load; long requests make round-robin uneven (Ch. 14.3, "Try it: why did the servers get uneven?") |
| 22 | Consistent hashing ✅ | deep | code | `Ring(nodes, vnodes=100)` with `node_for(key)`, `add`, `remove`; adding a 5th node moves about 1/5 of 10,000 keys (test: between 12% and 30%), while `hash % n` moves about 80%; uses `hashlib.md5`, never `hash()` (randomised per process) (Ch. 14.4) |
| 23 | Pick C or A ✅ | deep | explain | for 4 features of Taskboard (assigning tasks under the WIP limit, the activity feed, the unread counter, billing) choose consistency or availability during a partition and say what the user sees (Ch. 15.3–15.6, "Try it: pick C or A") |
| 24 | URL shortener codes ✅ | applied | code | `encode(n)`/`decode(code)` in base62; `Shortener` issuing codes from a counter, custom aliases validated (allowed characters, length, reserved words, taken → error), the same long URL may get different codes (Ch. 16.4, "Try it: custom aliases") |

## H. Project (Ch. 19)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | Refactor where it hurts, and write it down ✅ | challenge | code | `assessment = "build"`. Given the route-heavy Taskboard of Ch. 2.2, deliver `create_app()` with a service layer, a repository and a unit of work, and **the HTTP safety-net tests must still pass unchanged**; service-level tests run with fakes in < 0.5 s; plus `ADR = """..."""` with Status/Context/Decision/Consequences/Alternatives sections (checked for structure only) and a `PAIN_LOG` list mapping each layer to the pain it removed |

## Counts check

Tiers: drill 1, 3, 11, 12, 17, 19 (6); applied 2, 4, 5, 6, 8, 9, 10, 18, 20, 21, 24 (11); deep 7, 14, 15, 16, 22, 23 (6); challenge 13, 25 (2). Total 25.
Kinds: trace 1, 10, 14, 17, 20 (5); explain 8, 16, 23 (3); code 17.

## Risks and open questions

- The module is about judgement; tests can only check the mechanical half. Keep the explain answers rich (`answer.md` with a model answer and the counter-arguments) so self-rating teaches.
- p022's percentage bounds must be checked on several seeds of key names when writing (md5 is deterministic, so one run is enough once the key list is fixed).
- p025's starting code should be the chapter's own Ch. 2.2 version (about 200 lines) copied into `starter.py`; the safety-net tests copied into the test file. Keep both identical to the chapter so the learner recognises them.
