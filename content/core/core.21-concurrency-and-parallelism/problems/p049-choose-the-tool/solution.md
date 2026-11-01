## Approach

The model answer is in `answer.md`. The reasoning behind it fits in one table:

| System | Mostly... | Tool | What bounds it |
|---|---|---|---|
| A. Scraper | waiting on one server | asyncio | the shop's rate limit (rate limiter + semaphore) |
| B. Thumbnailer | pure-Python computing | processes | number of cores |
| C. Telegram bot | waiting, thousands at once | asyncio | API limit, DB pool size |
| D. Log aggregator | waiting, plus cheap parsing | asyncio or a few threads | bounded queue to the sender |
| E. ML + upload | computing, then waiting | processes + asyncio | cores; bandwidth; disk space (bounded queue) |

Three rules produce every row:

1. **Waiting overlaps; computing needs cores.** Threads and asyncio let waits overlap on one
   core. Only processes (or C code / free-threaded builds that release the GIL) put Python
   computation on several cores.
2. **Every stage needs a limit, and the limit comes from outside**: a server's rules, the
   number of cores, network bandwidth, memory or disk. "Unlimited" is never the answer; a
   bounded queue between a fast stage and a slow stage is what turns "too fast" into "wait".
3. **Plan for the unhappy path**: a timeout on every external call, retries only for temporary
   errors, failures recorded instead of crashing the batch, and shutdown that cancels, awaits
   cleanup, and leaves no half-written output.

## Check your answer

- Did you pick processes **only** where pure-Python computing dominates (B, and the first half
  of E)?
- Did each system get a concrete limit with a reason for its size?
- Did A respect the shop's 10 requests/second (a *rate*), not only a number in flight?
- Did D and E have a **bounded** queue for back-pressure?
- Did you mention timeouts *and* what happens to the item that timed out?
- Did you say how shutdown avoids half-written files or lost work?
- Did E use two tools, connected (for example `run_in_executor` from async code)?

## Another way

Thinking in **stages** helps with mixed systems: draw the pipeline (read -> compute -> upload),
label each stage "waits" or "computes", give each stage its own executor or task pool sized for
its bottleneck, and connect stages with bounded queues. Frameworks like `concurrent.futures`,
`asyncio`, and later tools like Celery or Dask all implement this same picture at different
scales.
