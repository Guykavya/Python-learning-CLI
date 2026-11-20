# Problem plan: swe.09 Deployment, observability and operations (30 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `swe.09.p001`…`p030`.

**Mix:** 10 drill, 12 applied, 6 deep, 2 challenge. **Kinds:** 22 code, 5 trace, 3 explain.
**assessment:** explain = p029, trace = p026, fix = p027, build = p030.
**★ core set:** p003, p006, p013, p014, p015, p017, p019, p025, p026, p027, p028, p029, p030 (outcomes: trace one failing request through logs by its request ID; roll back a bad deployment).

**Testing notes**
- **Docker, Compose, Nginx, Gunicorn, Prometheus, systemd and GitHub Actions are never run by a test** (swe offline rule). Problems work on **their text** (a Dockerfile, a compose YAML read with `pyyaml`, a workflow YAML, an Nginx access-log line, Prometheus exposition text) or on a **Python model of their behaviour** (layer cache, leaky bucket, health checks, a deploy pointer). The chapter's tutorials with captured output remain the place to see the real tools.
- The service problems reuse the chapter's FastAPI service shape (Ch. 5.1: `Settings`, `ConfigError`, `JsonFormatter`, `RequestContext`, `Metrics`, `create_app(settings)`), tested with `TestClient` and `caplog`; the request id lives in a `contextvars.ContextVar`.
- **Deploys use a pointer file, not a symlink:** `releases/<version>/` folders and `current` written with `os.replace` (atomic on every OS). Symlinks need extra privileges on Windows, so no test creates one.
- Signals: no test sends real signals; graceful shutdown is driven by calling the handler function.
- Time is injected everywhere (backup rotation, SLO windows).

## A. Processes and configuration (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | How many workers? | drill | code | `worker_plan(cpus, app_kind, memory_mb, mb_per_worker)` → Gunicorn sync workers `2*cpus+1` capped by memory; Uvicorn workers = cpus for async; (Ch. 2.4, "Try it: how many workers?") |
| 2 | Signals and graceful shutdown | drill | explain | what `SIGTERM`, `SIGINT`, `SIGKILL` and `SIGHUP` mean to Gunicorn and to your app, why `SIGKILL` cannot be handled, what "graceful timeout" protects (Ch. 2.6, "Try it: why did the request die?"); checklist |
| 3 | Settings that fail fast | drill | code | `Settings.from_env(env: dict)` (Ch. 3.3): required `DATABASE_URL`, `SECRET_KEY` ≥ 32 chars, `PORT` int 1..65535, `LOG_LEVEL` from a set; **all** problems reported in one `ConfigError`; `repr(settings)` hides the secret |
| 4 | Who wins? | drill | trace | `⚠ HAND-TRACE` a default, a `.env` file, a compose `environment:` entry and a shell variable set the same names; write the final value of 5 settings (Ch. 3.2 order) |
| 5 | Read a `.env` file | drill | code | `parse_dotenv(text)`: comments, blank lines, `export ` prefix, single/double quotes, `=` inside values, no variable expansion; a malformed line raises `ValueError` with the line number |

## B. Docker and Compose, as text (Ch. 4–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | A Dockerfile linter | applied | code | `lint_dockerfile(text)` → findings: `:latest` or no tag, shell-form `CMD` (no `SIGTERM`, Ch. 5.5), `COPY . .` before installing requirements (cache), no `USER` (runs as root), secrets in `ENV`, `apt-get` without cleanup; the chapter's final Dockerfile (Ch. 5.2) → `[]` |
| 7 | Which layers rebuild? | applied | trace | `⚠ HAND-TRACE` a 9-line Dockerfile and three edits (change `app/main.py`, change `requirements.txt`, change the base tag); write the first step that misses the cache each time (Ch. 5.3, "Try it: why is this Dockerfile slow?") |
| 8 | What does exit code 137 mean? | drill | code | `explain_exit(code)` → text for 0, 1, 2, 126, 127, 128+n (`SIGKILL` 137 often out of memory, `SIGTERM` 143), using `signal.Signals` names (Ch. "Try it: exit code 137") |
| 9 | Check a compose file | applied | code | `check_compose(yaml_text)`: the web service `depends_on` the database with `condition: service_healthy`, the database has a `healthcheck`, data in a **named** volume, the database port not published to the host, secrets via `env_file` not inline; the chapter's compose file (Ch. 6.2) → `[]` |

## C. Nginx (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | Read the proxy's access log | applied | code | `parse_access_line(line)` for the chapter's log format (status, request time, upstream time, request id) and `summarise(lines)`: counts per status, slowest 3 requests, share of 5xx (Ch. "Try it: read the log") |
| 11 | 502 or 504? | drill | trace | `⚠ HAND-TRACE` 6 backend situations (process down, port wrong, app too slow for `proxy_read_timeout`, app crashes mid-response, healthy, one of two upstreams down); write what the client gets (Ch. 7.4) |
| 12 | Model `limit_req` | deep | code | `LimitReq(rate_per_s, burst, nodelay, clock)` as a leaky bucket: `allow(t) -> "pass" | "delayed" | 503`; burst and `nodelay` behave like Ch. 7.5's table; requests at given times |

## D. Logs and request IDs (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 13 | One JSON object per line | drill | code | `JsonFormatter` (Ch. 5.1/8.1): `ts`, `level`, `logger`, `msg`, `request_id` from the context var, `extra` fields, exceptions as a single string field; every line `json.loads`; no line breaks inside a record |
| 14 | A request id everywhere | applied | code | middleware sets the id (reuse a valid `X-Request-ID`, else new), echoes it in the response, logs `request finished` with status and duration, and an unhandled error returns only the id to the client (Ch. 8.2, chapter tests at Ch. 5.1) |
| 15 | Follow one failing request | applied | code | Outcome 1. `trace_request(lines, request_id)` over mixed JSON lines from web and worker (some not JSON, some from other requests): the ordered events of that request, the first `ERROR`, and the services it passed through; mirrors the `jq` tutorial (Ch. 8.3–8.4) |
| 16 | What is wrong with these log lines? | applied | explain | 6 log lines (a password, a whole request body, an f-string with no fields, a stack trace split over lines, `print`, an error logged at INFO); say what is wrong with each and the fix (Ch. "Try it: what is wrong with these log lines?") |

## E. Health, shutdown and metrics (Ch. 9–10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | Liveness and readiness | applied | code | `/healthz` (process alive, never touches the database) and `/readyz` (database reachable via an injected check, not draining); 503 with the failing check named (Ch. 9.1–9.3, "Try it: which check?") |
| 18 | Drain before you stop | deep | code | `Lifecycle`: `on_sigterm()` sets draining (readiness turns 503), in-flight requests are counted, `wait_idle(timeout)` returns when the count hits 0 or the timeout passes; new requests while draining are still served (Ch. 9.5) |
| 19 | Metrics with route templates | applied | code | the chapter's `Metrics`: a request counter by `method, route, status` (route **template** `/orders/{id}`, never the raw path), a latency histogram; `render()` in Prometheus text format; the test parses the text (Ch. 10.2) |
| 20 | Percentiles from a histogram | deep | code | `quantile(q, buckets)` from cumulative `le` buckets with linear interpolation (what `histogram_quantile` does); p50/p95/p99 on a skewed example; why the mean hides the tail (Ch. 10.4) |
| 21 | Which metric type? | drill | trace | `⚠ HAND-TRACE` 8 things to measure (requests served, queue length, latency, memory in use, errors, jobs in flight, …); write `counter`, `gauge` or `histogram` (Ch. "Try it: which metric type?") |
| 22 | Error budgets and burn rate | deep | code | `budget(slo=0.999, total, failed)` → allowed failures and remaining share; `should_page(windows)` with a fast-burn (1 h) and slow-burn (6 h) rule (Ch. 10.5–10.7) |

## F. CI, deploys and rollback (Ch. 11–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 23 | Lint a CI workflow | applied | code | `check(workflow: dict)` (the chapter's function, Ch. 11.5): actions pinned to a version, `timeout-minutes` on every job, `permissions` set, the cache key hashes the lock file, the test job runs the same command as `make test`; returns `(severity, message)` pairs |
| 24 | RPO and RTO from a plan | drill | code | `worst_case_loss(backup_times, failure_time)` (minutes since the last good backup) and `restore_time(size_gb, mb_per_s, fixed_minutes)`; compare with targets (Ch. "Try it: RPO and RTO") |
| 25 | Deploy with automatic rollback | challenge | code | Outcome 2. `deploy(root, version, files, health_check)`: write `releases/<version>/`, switch the `current` pointer atomically, run the health check (injected), on failure **switch back** and keep the failed release for inspection; keep the last 5 releases; a second failure in a row still leaves the last good version live (Ch. 12.3) |
| 26 | Why did the rollback work? | deep | trace | `assessment = "trace"`. `⚠ HAND-TRACE` a timeline of 5 deploys, one with an additive migration and one with a destructive one; write which version is live after each step and whether "roll back" is still safe or "roll forward" is needed (Ch. 12.4, "Try it: roll forward or back?") |
| 27 | Fix the deploy that leaves a broken release live | applied | code | `assessment = "fix"`. The given script switches `current` before the health check, does not restore on failure, and deletes the previous release first; tests: a failing health check leaves the old version live and untouched, and the pointer never names a half-written folder |

## G. Backups and operations (Ch. 13–14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 28 | Backups with rotation and a drill | applied | code | `backup(db_file, backup_dir, keep=7, now)` with `sqlite3.Connection.backup`, timestamped names, oldest beyond `keep` removed; `drill(backup_file, min_orders)` restores into a temp file and checks integrity and a minimum row count (Ch. 13.2) |
| 29 | Roll back or forward, and the first five minutes | deep | explain | `assessment = "explain"`. For an alert "5xx at 30% after deploy 1.4.2": the first five minutes (stabilise, communicate, find the request ids), the decision rule for rolling back, what goes into the postmortem (Ch. 12, 14.1–14.2, "Try it: first five minutes") |

## H. Project (Ch. 15)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 30 | Operate the API | challenge | code | `assessment = "build"`. `create_app(settings)` with fail-fast settings, JSON logs with request ids, `/healthz` and `/readyz`, `/metrics` with route templates, graceful draining; plus `DOCKERFILE`, `COMPOSE` and `WORKFLOW` text constants that must pass the p006, p009 and p023 checkers (bundled in the test). Tests: a failing request is traceable by id end to end, readiness flips during drain, metrics count the 500, the deployment texts are clean |

## Counts check

Tiers: drill 1, 2, 3, 4, 5, 8, 11, 13, 21, 24 (10); applied 6, 7, 9, 10, 14, 15, 16, 17, 19, 23, 27, 28 (12); deep 12, 18, 20, 22, 26, 29 (6); challenge 25, 30 (2). Total 30.
Kinds: trace 4, 7, 11, 21, 26 (5); explain 2, 16, 29 (3); code 22.

## Risks and open questions

- The Dockerfile/compose/workflow checkers are **teaching subsets**; `problem.md` lists their exact rules so a learner's correct-but-different file is not punished for a rule that is not listed.
- p007 and p011 describe Docker and Nginx behaviour: base the expected answers on the chapter's captured tutorial output, not on memory.
- p020's interpolation must match the chapter's description of `histogram_quantile`; if the chapter does not define it precisely, state the formula in `problem.md`.
