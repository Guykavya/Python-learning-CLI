# SWE capstone: a production-grade backend service

You have finished (or nearly finished) the Software Engineer track. The capstone proves
you can combine it: design a backend service, build it, test it, ship it in a container,
and show that you can see inside it when it breaks. You choose the idea. Nobody gives you
a solution. The checklist at the bottom is how you (or a reviewer) decide it is done.

Syllabus line: *Production-grade backend service (FastAPI, Postgres, Redis, Docker, CI,
tests, monitoring).*

## Rules

- **It is yours.** Your idea, your design, your code. Use the course chapters and the
  official docs, not generated code. A reviewer (a friend, or Claude in tutor mode)
  reads and comments; they do not rewrite it.
- **Own folder, own repo.** Keep it outside `my-work/`, with its own git history on your
  personal GitHub. Never a company account or company remote. Never a company database,
  company API key or company data.
- **FastAPI is the default framework.** Flask or Django is fine if you can defend the
  choice in `DESIGN.md` (swe.06 taught you how). The checklist below is framework-neutral.
- **Offline-first.** The test suite must run with **no network, no Docker and no running
  Postgres or Redis**. Tests use SQLite and in-process fakes (swe.03, swe.08 showed how).
  Postgres, Redis and Docker are for the *run it for real* path (part G), where you prove
  the same code works on the real services.
- **Size.** About 1,500-4,000 lines of code, plus tests. Smaller than that and it is a
  tutorial app; much bigger and you will never finish.
- **Time-box.** Plan 3-5 weeks of part-time work. Write the design note first (below).

## Pick an idea

Choose something with **real rules, several kinds of users or data, and at least one thing
that must not happen twice or must not leak**. A CRUD list is a toy. Examples:

- A booking service (rooms, seats, slots) where two people must never get the same slot.
- A wallet or expense-sharing service where money moves between accounts exactly once.
- A URL shortener with per-user links, click analytics and rate limits.
- A job-board or marketplace API with owners, applicants and an approval flow.
- A small order system: catalogue, cart, order, stock, payment callback.
- A notes or file-sharing service with sharing rules (private, shared, public).

If you cannot decide in a day, take the default: **a booking service** (users, resources,
bookings, cancellations, a daily report job). It touches every part of the track.

## Step 0: the design note (2 pages, before any code)

Write `DESIGN.md` and keep it in the repo:

1. One-sentence purpose, who uses it, and the three most important rules the service
   enforces (for example, "no double booking").
2. The API: every endpoint with method, path, who may call it, request and response shape
   and the error cases.
3. The data model: tables, keys, indexes and why. Draw it (ASCII is fine).
4. The auth model: who the roles are and how ownership is checked.
5. The slow or failure-prone parts: what goes to a queue or cache, and what happens when a
   task runs twice or Redis is down.
6. The layers you will use, and the concrete pain each one removes (swe.10: add a layer
   only when it pays off).
7. How you will test it and how you will deploy it.
8. The risks: your three biggest unknowns and what you will try first.
9. What you are deliberately *not* building.

Bring `DESIGN.md` to the reviewer before you write much code.

## Requirements

Tick every **Must**. Aim for most **Should** items. **Stretch** is optional.

### A. API and design

- **Must:** at least **10 endpoints** across at least **3 resources**, with consistent
  naming, correct HTTP methods and correct status codes (201 on create, 404, 409, 422,
  never a 200 that hides an error).
- **Must:** request and response bodies are validated models; the OpenAPI docs page lists
  every endpoint with examples.
- **Must:** list endpoints are **paginated** and have at least one filter.
- **Must:** one **consistent error format** for every failure, with a stable error code.
- **Must:** the API is versioned (`/v1/...`) and `DESIGN.md` says what counts as a breaking
  change.
- **Should:** an idempotency key on the one endpoint where a double call would hurt.
- **Stretch:** a second client of the same API (a small CLI that uses `httpx`).

### B. Data

- **Must:** a schema with foreign keys, uniqueness and `NOT NULL` where the rules need
  them, so the **database** also refuses bad data, not only your Python.
- **Must:** schema changes through **migrations** (Alembic), never by editing tables by
  hand. Include at least one migration that changes existing data safely.
- **Must:** a transaction around every multi-step change; a test proves that a failure
  half-way leaves **nothing** changed.
- **Must:** at least one index you can justify by showing the query plan before and after.
- **Must:** no N+1 queries on your list endpoints; a test counts the queries.
- **Should:** a seed script that creates demo data.
- **Should:** a documented backup and restore step that you actually tried once.
- **Stretch:** one concurrency test that shows your "no double booking" rule holds when two
  requests race.

### C. Auth and security

- **Must:** passwords hashed with a proper algorithm; no secret in the repo, all secrets
  from environment settings; a `.env.example` with fake values.
- **Must:** every non-public endpoint requires authentication.
- **Must:** **ownership checks**: a test proves user B cannot read, change or delete user
  A's data, on every resource that has an owner.
- **Must:** role checks for at least one admin-only action, with a test for the refusal.
- **Must:** a rate limit on the login endpoint (or the most abusable one), with a test.
- **Should:** the OWASP Top 10 walked through in `SECURITY.md`: one line per item saying
  how the service handles it or why it does not apply.
- **Should:** tokens that expire, and a test for the expired case.
- **Stretch:** refresh tokens or a logout that really invalidates a session.

### D. Caching, queues and background work

- **Must:** at least one **background job** (report, email stub, clean-up) that is safe to
  run twice: a test runs it twice and checks the result is the same as once.
- **Must:** at least one **cache** with a clear invalidation rule, and a test that shows a
  stale value cannot survive an update.
- **Must:** the service still works, only slower, when the cache is unavailable (a test
  with a broken fake cache).
- **Should:** retries with backoff and a place for failed jobs to land (dead-letter list).
- **Should:** a scheduled job, with the schedule written down.
- **Stretch:** the same job running on a real queue (Redis with RQ or arq) as well as the
  in-process fake.

### E. Testing

- **Must:** the suite runs with one command (`make test` or `pytest`) and needs no network.
- **Must:** unit tests for the business rules, plus API tests that go through the HTTP
  layer using the framework test client.
- **Must:** every Must in parts A to D that says "a test" has one, and the test **name**
  says the rule (`test_user_cannot_read_other_users_booking`).
- **Must:** coverage measured; at least **80 percent** on the code that holds rules, and
  you can explain every uncovered line that is left.
- **Must:** tests are independent: they pass in any order and in a fresh database.
- **Should:** one test per error code in your error format.
- **Should:** `ruff` (or flake8), a formatter and `mypy` clean in CI.
- **Stretch:** a mutation check: break one rule on purpose, confirm a test fails.

### F. Observability and operations

- **Must:** **structured logs** (JSON lines) with a **request ID** on every line of a
  request, and the same ID returned in a response header.
- **Must:** `/health` (is the process up) and `/ready` (are database and cache reachable)
  endpoints, with tests.
- **Must:** basic metrics: request count, error count and latency, readable at `/metrics`
  or in a log summary.
- **Must:** `RUNBOOK.md` with: how to start, stop and roll back; what each alert or log
  line means; and how to trace one failing request by its request ID. Use it yourself to
  trace one deliberately failing request, and paste the log lines into the runbook.
- **Should:** graceful shutdown, so in-flight requests finish.
- **Should:** a log line for every slow query above a threshold you chose.
- **Stretch:** a small dashboard or a script that prints p50 and p95 latency.

### G. Packaging, deployment and CI

- **Must:** a `Dockerfile` (small image, non-root user, no secrets baked in) and a
  `docker-compose.yml` that starts the app, Postgres and Redis.
- **Must:** configuration from environment variables only, one place that reads them,
  failing fast with a clear message when a required setting is missing.
- **Must:** **run it for real once**: start the compose stack, run the migrations on
  Postgres, run the demo requests, and paste the commands and output into
  `docs/real-run.md`. Machine-specific values (ids, timestamps) are marked as such.
- **Must:** a CI file (GitHub Actions) that installs, lints, type-checks and runs the tests.
  If you cannot push, the file still has to be correct; the reviewer reads it.
- **Must:** one **rollback drill**: deploy version 2 with a bad change, roll back to
  version 1, and write what you did in the runbook.
- **Should:** a `Makefile` with `install`, `test`, `lint`, `run`, `migrate`, `seed`.
- **Should:** a health check inside the compose file.
- **Stretch:** a multi-stage Docker build with a measured image-size comparison.

### H. Documentation

- **Must:** `README.md` with: what it is, a diagram of the parts, setup in 5 commands, how
  to run the tests, how to run with Docker, and a worked example request with the answer.
- **Must:** `DESIGN.md` updated to match what you actually built, including what you
  changed from the first draft and why.
- **Must:** `RUNBOOK.md` (part F) and `docs/real-run.md` (part G).
- **Should:** an `ADR` file or section with at least three decisions: the options you
  weighed and why you chose one.
- **Should:** "Known limits" and "What I would do next".
- **Stretch:** a one-page system-design sketch for 100 times your expected traffic.

### I. Engineering habits

- **Must:** git history with many small commits, clear messages, work done on branches
  and merged (swe.01), not one giant commit.
- **Must:** no secrets, no personal data and no machine paths in the repo or the history.
- **Should:** a `CHANGELOG.md` and a version tag for the release you deploy.
- **Stretch:** a short self-review: read your own diff as a reviewer and list five things
  you would change.

## How the review works

1. **Design review** (before coding): the reviewer reads `DESIGN.md` and asks questions.
   Typical outcomes: "too big, cut X", "what stops two requests taking the same slot?", or
   "which rule does this layer protect?".
2. **Midpoint check:** the data model, auth and about half the endpoints are done with
   tests. The reviewer runs the suite and tries to break the rules with their own requests.
3. **Final review:** run through the checklist above. For every unticked **Must** the
   reviewer gives a pointer, not a patch ("what happens to the stock if the payment
   callback arrives twice?").
4. **Fresh-machine test:** clone the repo into a new folder, follow only the README, and
   run the tests and the compose stack. If you get stuck, the README is the bug.
5. **Incident drill:** the reviewer names a failure ("the database is slow", "Redis is
   down", "a user says their booking vanished"). You use only your logs, metrics and
   runbook to find the cause. If you cannot, the observability is the bug.

### Scoring (for yourself)

| Score | Meaning |
|---|---|
| All Musts, most Shoulds | SWE capstone passed |
| All Musts only | Passed, but go back and add the missing polish and tests |
| Any Must missing | Not done yet. Finish those first |

Stretch items are for pride and for your portfolio, not for the pass mark.

## Why this capstone

Anyone can follow a framework tutorial. A service that refuses to double-book, keeps one
user out of another's data, survives a task running twice, and can be debugged from its
own logs at 2 a.m. is what a backend engineer is paid for. The ownership test, the
run-it-twice test and the request-ID trace are the three habits to keep for life.
