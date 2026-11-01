## Hint 1

For each workload, picture the program while it is slow. Is the CPU busy (the fan spins, one
core shows 100 %), or is the program sitting there until bytes arrive? Busy means CPU-bound,
sitting means I/O-bound. Does any workload have **two** stages with different answers?

## Hint 2

Then use this small decision table:

```
waiting, a library with async support, many connections  -> asyncio
waiting, only blocking libraries, tens of jobs           -> threads (ThreadPoolExecutor)
computing in Python code                                  -> processes (ProcessPoolExecutor)
waiting AND computing                                     -> both, one per stage
tiny job                                                  -> nothing at all
```

Workloads 5 and 8 are the ones people get wrong. What happens to an event loop when you call a
blocking function inside it?
