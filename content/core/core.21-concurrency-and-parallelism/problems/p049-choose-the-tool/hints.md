## Hint 1

Start every system with one question: **while this program runs, what is it mostly doing:
waiting (network, disk, users) or computing?** Waiting means threads or asyncio; computing in
pure Python means processes (the GIL). If the answer is "both", the system has two halves, and
each half gets its own tool.

## Hint 2

Then go through the same checklist for each one:

```
tool:        waiting -> asyncio (many waits) or threads (few, or sync-only libraries)
             computing -> ProcessPoolExecutor(cores)
bound:       Semaphore(N) / pool size / RateLimiter; what sets N? (server rules, cores, bandwidth, memory)
backpressure: bounded Queue(maxsize) between fast and slow stages
timeout:     asyncio.timeout per unit + retry 5xx/transport with backoff; record failures, keep going
shutdown:    cancel, await cleanup (finally), no half-written files (.part + rename), resumable
why not X:   GIL? memory per thread/process? pickling cost? loop blocked by CPU work?
```
