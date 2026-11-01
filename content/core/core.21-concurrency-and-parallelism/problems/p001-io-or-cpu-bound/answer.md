1. **Download 200 pages: I/O-bound. asyncio (or threads).** Each request spends almost all its
   time waiting for the network; many waits can overlap in one thread. Limit it (say 10 to 20 at
   once) to be polite to the server.
2. **Resize 5,000 photos: CPU-bound. Processes** (`ProcessPoolExecutor`, one worker per core).
   The work is maths on pixels. Threads in GIL Python would take turns on one core. (Pillow
   releases the GIL inside some C code, so threads help a little there, but processes are the
   safe choice.)
3. **Parse a 2 GB log: CPU-bound** (the regex work), with some disk reading. **Processes**,
   each taking a chunk of the file (by byte offsets or by splitting the file first). One
   process reading it straight through is also fine if it is fast enough: measure first.
4. **Chat server, 3,000 connections: I/O-bound. asyncio.** Each user is idle most of the time.
   3,000 threads would cost a lot of memory and switching; 3,000 tasks are cheap.
5. **Weather API with a blocking library: I/O-bound. Threads** (`ThreadPoolExecutor`, about
   10 workers). Blocking calls would freeze an asyncio loop, and while a thread waits on the
   network it releases the GIL, so the others run. (Inside an asyncio program, the same idea is
   `asyncio.to_thread`.)
6. **Prime checks: CPU-bound. Processes.** Pure Python loops hold the GIL, so threads give no
   speed-up at all. Split the numbers into chunks, one chunk per worker.
7. **One small config file: neither matters. No concurrency.** Reading 2 KB takes well under a
   millisecond. Concurrency would add complexity and save nothing.
8. **Download then extract: both, in stages. asyncio (or threads) for downloads, processes for
   the text work.** The two halves have different bottlenecks, so give each the right tool:
   download with a limited number of requests in flight, then send each file to a
   `ProcessPoolExecutor` (from async code: `loop.run_in_executor`).

**Rule of thumb:** waiting → threads or asyncio (asyncio for very many connections, threads
when the library is blocking); computing → processes; a mix → a pipeline that uses both.
On a free-threaded build (`python3.14t`) threads can also run Python code in parallel, but the
I/O-or-CPU question still decides how many workers make sense.
