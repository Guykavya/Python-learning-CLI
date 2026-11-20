# Problem plan: swe.08 Caching, queues and background work (30 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `swe.08.p001`…`p030`.

**Mix:** 10 drill, 12 applied, 6 deep, 2 challenge. **Kinds:** 21 code, 6 trace, 3 explain.
**assessment:** explain = p017, trace = p023, fix = p007, build = p030.
**★ core set:** p002, p004, p006, p007, p012, p017, p018, p019, p022, p023, p027, p030 (outcome: a worker that gives the same result when a task runs twice).

**Testing notes**
- **No Redis server, no `redis`/`fakeredis` package.** The chapter's `MiniRedis` (Ch. 3.2: strings, `SET NX EX`, `INCR`, `EXPIRE`, `TTL`, hashes, sorted sets, with an injected clock) goes into `conftest.py` for every problem except p004, where the learner writes the subset. `problem.md` shows its interface; the real Redis commands are named so the knowledge transfers.
- **Queues run on SQLite** files in `tmp_path` (the chapter's `JobQueue`, Ch. 9). Workers are driven step by step (`worker.run_once()`), not as background threads, except p012/p019 which use 2–20 threads with joins and timeouts.
- **Crashes are simulated** with the chapter's `Crash(BaseException)` and `CrashAt(point)` (Ch. 11.4) and a `FakeMailProvider` that records sends and can time out after sending; never `os.kill`. The chapter's `kill -9` demo (Ch. 16.4) stays a "Try it on your machine".
- Time is a fake clock everywhere (TTL, leases, backoff, cron).
- **Celery** (p026) is installed and imports in 0.3 s, but in eager mode (`task_always_eager`) `autoretry_for` raises `celery.exceptions.Retry` instead of retrying (measured 2026-11-18), so tests check the task's **options** (`acks_late`, `max_retries`, `autoretry_for`, `retry_backoff`) and the eager success path only, never real retries or a broker.

## A. Caching basics (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Cache or queue? | drill | trace | `⚠ HAND-TRACE` 8 situations (slow product page, sending 10,000 e-mails, a report that takes 2 minutes, a rate limit, …); write `cache`, `queue`, `both` or `neither` (Ch. "Try it: cache or queue?") |
| 2 | A TTL + LRU cache | drill | code | `TTLCache(maxsize, ttl, clock)` (Ch. 2.5): `get` returns `None` after expiry, `set` evicts the least recently **used**, a `get` refreshes recency; hits/misses counted |
| 3 | Is the cache paying off? | drill | code | `hit_ratio(events)` and `mean_latency(ratio, hit_ms, miss_ms)`; `break_even_ratio(...)` when a cache lookup itself costs time (Ch. 2.1, "Try it: size the cache") |
| 4 | MiniRedis, the core commands | applied | code | `SET` with `ex=` and `nx=`, `GET`, `DEL`, `INCR` (error on non-integers), `EXPIRE`, `TTL` (−2 missing, −1 no expiry) with a fake clock; lazy expiry on read |
| 5 | Why is `INCR` safe? | drill | explain | single-threaded command execution, read-modify-write in one command vs `GET` then `SET` from two clients (Ch. "Try it: why is INCR safe?"); checklist |

## B. Cache-aside, keys and invalidation (Ch. 4–5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | A catalogue behind a cache | applied | code | `Catalog(db, cache, ttl=300)`: cache-aside `get_product`; a missing product is cached as "not found" for 30 s (Ch. "Try it: why the 404 is cached"); the fake database counts reads |
| 7 | Fix the shared cache key | applied | code | `assessment = "fix"`. Prices depend on the customer's tier but are cached under `product:{id}`, so Ravi sees Asha's member price (Ch. 4.4). Fix the key; tests alternate users and check each sees their own price and that public data is still shared |
| 8 | Good cache keys | drill | code | `cache_key(namespace, version, **params)`: sorted params, `None` dropped, long keys hashed with SHA-256, no spaces; the same params in any order give the same key |
| 9 | Delete-after-write is not enough | deep | trace | `⚠ HAND-TRACE` the chapter's interleaving runner (Ch. 5.2): for the 6 interleavings of a reader (read DB, store) and a writer (update DB, delete cache), write the final cache value; mark the stale ones |
| 10 | Invalidate with a generation number | applied | code | keys `product:{id}:g{gen}`; a write bumps `gen` with `INCR`; old entries are never read again and expire by TTL (Ch. 5.3); the race of p009 no longer leaves a stale value (the test replays the interleavings) |

## C. Stampedes and other Redis jobs (Ch. 6–7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 11 | Count the loads | drill | trace | `⚠ HAND-TRACE` 20 requests miss at once; write how many times the loader runs with `get_naive` and with `get_single_flight` (Ch. "Try it: count the loads"); confirm by running when writing |
| 12 | Single flight with a lock | deep | code | `get_single_flight(cache, key, loader, ttl, lock_ttl)` using `SET NX EX` as a lock; 20 threads → loader runs once, all get the value; a loader that raises releases the lock |
| 13 | Stale-while-revalidate and TTL jitter | deep | code | `get_swr(key, soft, hard)`: fresh → cached; soft-expired → serve stale and refresh once; hard-expired → load; TTLs get ±10% jitter from an injected `rng` (Ch. 6.2) |
| 14 | `BackgroundTasks` is not a queue | drill | explain | what is lost on a crash or deploy, what a durable queue adds (persistence, retries, many workers) and what belongs in a job payload (ids, not objects) (Ch. 8.2–8.3); checklist |
| 15 | A shared rate limit that holds | applied | code | `hit_unsafe` lets 2 workers both pass at the limit; `hit_safe` uses `INCR` + `EXPIRE` on first hit (Ch. 7.2); the test interleaves two "workers" deterministically |
| 16 | The lock bug | deep | code | `release_naive` deletes a lock another worker now holds (Ch. 7.3, "Try it: spot the lock bug"); write `acquire(token)`/`release(token)` that only deletes its own lock (compare token, then delete, in one MiniRedis call `delete_if_equals`) |

## D. Queues, workers and delivery (Ch. 8–10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | Pick the delivery guarantee | applied | explain | `assessment = "explain"`. At-most-once, at-least-once, "exactly-once effect"; ack before or after work and what each loses or duplicates; why duplicates are normal (Ch. 8.4, 11.1, "Try it: pick the guarantee") |
| 18 | A durable job queue on SQLite | applied | code | `JobQueue(path, clock)`: `enqueue(kind, payload, run_at=None, dedupe_key=None)`, `claim(worker)` (oldest due job, lease 30 s, one transaction), `ack`, `fail`; delayed jobs wait; a dedupe key enqueued twice gives one job (Ch. 9.2–9.4) |
| 19 | Leases and the worker name | deep | code | a worker that crashed leaves a leased job; after the lease the job is claimable again; the old worker's late `ack` is rejected because the name no longer matches (Ch. 9.5, "Try it: why check the worker name?"); 4 threads claiming 200 jobs → no job claimed twice |
| 20 | What happens to the job? | applied | trace | `⚠ HAND-TRACE` 6 handler outcomes (success, `RetryLater`, `PermanentError`, `KeyError`, timeout, success on attempt 5 of 5); write status, attempts and `run_at` offset (Ch. 10.1, "Try it: classify the error") |
| 21 | Backoff, dead letters and redrive | applied | code | `backoff_delay(attempt, base, cap, rng)` (Ch. 12.1); after `max_attempts` the job goes to `dead` with the last error; `redrive(job_id)` resets attempts; redriving a job whose effect already happened is safe only with p022's rule |

## E. Idempotent workers (Ch. 11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 22 | An e-mail worker that survives crashes | challenge | code | Outcome. `make_safe_handler(db_path, provider)` (Ch. 11.5): records intent in an e-mail log with a unique key, passes the key to the provider, marks sent afterwards. The test runs the job with **every** crash point (`before_send`, `after_send_before_mark`, `after_mark_before_ack`) and with duplicate deliveries: each customer gets exactly one e-mail |
| 23 | Which crash window? | deep | trace | `assessment = "trace"`. `⚠ HAND-TRACE` the **naive** handler (Ch. 11.4) with a crash at each of 4 points and one retry; write how many e-mails each customer receives (Ch. "Try it: which window?") |
| 24 | The outbox | applied | code | `place_order(conn, order)` writes the order **and** an outbox row in one transaction; `relay(conn, queue)` moves unsent outbox rows to the queue and marks them; a crash between relay steps sends at most one duplicate, which the dedupe key absorbs (Ch. 11.7) |
| 25 | A deterministic, atomic report | drill | code | `build_report(rows, month)` returns the same bytes for the same input (sorted rows, no timestamps); `write_atomic(path, data)` via a temp file and `os.replace`; a crash mid-write leaves the old file intact (Ch. 11.8) |

## F. Libraries, schedules, operations (Ch. 13–15)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 26 | A Celery task configured for crashes | applied | code | define `app = Celery(..., broker="memory://")` and `send_welcome_email` with `acks_late=True`, `reject_on_worker_lost=True`, `autoretry_for=(ProviderTimeout,)`, `max_retries=5`, `retry_backoff=True` and an idempotency key argument (Ch. 13.2, "Try it: read the config"); the test inspects the options and runs it once in eager mode |
| 27 | Parse a cron expression | applied | code | `Cron("*/15 9-17 * * 1-5")` (Ch. 14.1): `parse_field` with `*`, lists, ranges, steps; `next_run(after)` in a given `ZoneInfo`; invalid fields raise `ValueError` naming the field |
| 28 | When does it run next? | drill | trace | `⚠ HAND-TRACE` 5 cron lines and a start time, including a daily 02:30 job on a DST change day in `Europe/London`; write the next run time (Ch. 14.2, "Try it: next run"); confirm by running when writing |
| 29 | How many workers? | drill | code | `workers_needed(arrival_per_s, seconds_per_job, target_utilisation=0.7)` from Little's law, and `admit(queue_length, limit)` for backpressure (503 + `Retry-After`) (Ch. 15.3–15.4) |

## G. Project (Ch. 16)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 30 | An e-mail and report worker that survives crashes | challenge | code | `assessment = "build"`. The p018 queue, the p022 e-mail handler, the p025 report handler, retries with dead letters, and `GET /jobs/{id}` status in a small FastAPI app (`TestClient`). Tests "kill it everywhere": crash points in both handlers, duplicate deliveries, a provider outage that ends in `dead` then a redrive; final state: one e-mail per user, each report file complete and identical to a clean run |

## Counts check

Tiers: drill 1, 2, 3, 5, 8, 11, 14, 25, 28, 29 (10); applied 4, 6, 7, 10, 15, 17, 18, 20, 21, 24, 26, 27 (12); deep 9, 12, 13, 16, 19, 23 (6); challenge 22, 30 (2). Total 30.
Kinds: trace 1, 9, 11, 20, 23, 28 (6); explain 5, 14, 17 (3); code 21.

## Risks and open questions

- Thread tests (p012, p019) must not depend on scheduling luck: use a `threading.Barrier` to start threads together and assert only invariants (loader calls == 1, no double claim).
- p028's DST answer must be produced by running the reference with `zoneinfo`; Windows needs the `tzdata` package (already a dependency on win32).
- MiniRedis differs from Redis in performance and in having no persistence; `problem.md` of p004 lists exactly which behaviours match real Redis.
