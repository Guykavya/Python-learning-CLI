## Hint 1

Ask two questions for each line:

1. Is there an `await` on something that **pauses** (an async sleep, async I/O)? Only there
   can the loop run other tasks.
2. If not, how long does the line keep the thread busy? Microseconds are fine; tenths of a
   second are not.

Then sort the blocking ones into "waiting" (network, disk, `sleep`: a thread fixes it) and
"computing" (loops, `sum`: only a process fixes it, because of the GIL).

## Hint 2

Template answers:

```
waiting on I/O, sync library   -> blocks; await asyncio.to_thread(func, args)  or an async library
await <async thing>            -> does not block; the task pauses, the loop runs others
pure CPU, long                 -> blocks; await loop.run_in_executor(process_pool, func, args)
tiny and fast                  -> technically blocks for microseconds; fine to leave
```

`requests` and `sqlite3` have no `await` anywhere: what does that tell you? Which async
libraries replace them?
