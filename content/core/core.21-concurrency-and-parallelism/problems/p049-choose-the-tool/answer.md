**A. Scraper: asyncio (httpx.AsyncClient), parsing inline.**
The work is waiting on the network; parsing is a few ms, too small to be worth moving off the
loop. **Bounding:** the shop's limit is the real constraint, so a rate limiter (10 starts per
second, like p040) plus an `asyncio.Semaphore(10)` on requests in flight. Feed URLs through a
bounded `asyncio.Queue` to ~10 worker tasks so 10,000 tasks are not created at once and the
writer cannot fall behind unnoticed. **Timeouts:** `asyncio.timeout(15)` per page; retry 5xx and
transport errors with exponential backoff (2-3 times), never 4xx; record failures and keep
going. **Shutdown:** Ctrl+C cancels the main task; the TaskGroup cancels the workers, `finally`
blocks flush what was saved, and a "done" set lets the next run resume. **Not threads:** they
would work for 10 connections, but asyncio makes the rate limit, timeouts and cancellation much
easier. **Not processes:** nothing is CPU-bound.

**B. Thumbnailer: processes (`ProcessPoolExecutor(max_workers=8)`).**
Pure-Python image work is CPU-bound, and the GIL lets only one thread run Python bytecode at a
time, so threads would use one core. Eight processes use eight cores. **Bounding:** the pool
size (number of cores) bounds the work; submit file **paths**, not 5 MB images (pickling big
data between processes is slow), and use `executor.map(..., chunksize=20)` or submit in batches
so 5,000 futures and results do not pile up. Each worker reads and writes its own files.
**Timeouts / failures:** a corrupt photo raises in the worker; catch it per file in the worker
function and return an error record so one bad file does not stop the batch. A worker cannot be
interrupted from outside, so a "per image timeout" is enforced with `future.result(timeout=...)`
only as a report; truly stuck work needs the pool shut down. **Shutdown:**
`shutdown(cancel_futures=True)` drops queued photos; write each thumbnail to a temporary name
and rename, so a killed run leaves no half-written files and can be resumed. **Not asyncio:** no
waiting to overlap. **Not threads:** the GIL (unless a free-threaded 3.14t build is used and the
library supports it).

**C. Telegram bot: asyncio, one event loop, async HTTP and an async DB driver.**
Thousands of conversations each spend seconds waiting on the AI API: classic I/O-bound work
with very many simultaneous waits. A task per message is cheap (kilobytes), a thread per
message is not. **Bounding:** an `asyncio.Semaphore(50)` (or the API's documented limit) around
AI calls, and a connection pool of ~10 for the database (a semaphore or the driver's own pool).
Per-user ordering: a small `asyncio.Lock` or queue per chat, so two quick messages from one user
are answered in order. **Timeouts:** `asyncio.timeout(20)` per AI call; on timeout reply "Sorry,
that took too long" instead of silence; retry once on 5xx. **Shutdown:** stop taking updates,
cancel in-flight handlers (their `finally` closes DB connections), then close the HTTP client.
If only a sync DB library exists, call it with `asyncio.to_thread`. **Not threads:** thousands
of threads cost memory and context switches and make cancellation hard. **Not processes:**
nothing CPU-heavy.

**D. Log aggregator: asyncio (or a few threads), regex parsing inline.**
Mostly waiting: for new lines and for the network. Regex on one line takes microseconds, so it
is fine on the loop (the thousands of lines per second it costs are small). Tailing files has no
real async API on Linux, so either read in a thread per file via `asyncio.to_thread` /
a small thread pool, or poll the files every 0.2 s from the loop. **Bounding / back-pressure:**
readers put parsed lines into a **bounded** `asyncio.Queue(maxsize=10_000)`; a single sender
task drains it every second into one batch. If the central server is down, the queue fills and
readers wait (back-pressure) instead of eating all memory; alternatively drop oldest lines and
count them. **Timeouts:** `asyncio.timeout(5)` per batch upload, retry with backoff, keep the
batch until it is acknowledged. **Shutdown:** stop readers, flush the queue in one last batch,
then exit. **Not processes:** parsing is cheap; 40 processes only add overhead. Plain
threads would also work (40 file threads + `queue.Queue(maxsize=...)` + one sender), simpler if
the team does not know asyncio, but timeouts and clean cancellation are harder.

**E. ML preprocessing + upload: a mix, processes for crunching, asyncio (or threads) for
uploading, connected by a bounded queue.**
The two halves are different kinds of work. Turning CSV rows into features in pure Python is
CPU-bound: `ProcessPoolExecutor(max_workers=cores - 1)`, one CSV file (or chunk) per job,
workers write their result file to disk and return only the path (do not send 1 GB through a
pipe). Uploading is I/O-bound: an asyncio loop calls `loop.run_in_executor(process_pool, ...)`
for each file and, as results arrive, uploads with an async client, `asyncio.Semaphore(4)`
(bandwidth, not CPU, is the limit). **Back-pressure:** each result is 1 GB on disk, so limit
how many finished-but-not-uploaded files may exist (a bounded queue of paths, size ~4); the
producer side stops submitting when it is full. **Timeouts:** long per-upload timeouts
(minutes) with retries and resumable/multipart uploads; a failed preprocessing job is logged
with its input file and retried later. **Shutdown:** cancel the queued jobs
(`cancel_futures=True`), let running ones finish or kill the pool, cancel uploads and delete
partial uploads; uploaded files are recorded so the run resumes. **Why not one tool:** threads
alone would crunch on one core; processes alone would waste a process per upload; asyncio alone
would freeze its loop during the number crunching.
