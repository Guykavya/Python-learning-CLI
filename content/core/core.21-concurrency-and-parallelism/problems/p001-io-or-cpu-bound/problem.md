# Explain: I/O-bound or CPU-bound?

Before you pick threads, processes or asyncio, ask one question: **while this program is
slow, what is the CPU doing?**

- If it is mostly **waiting** (for the network, the disk, a database, a user), the job is
  **I/O-bound**. Waiting can overlap: threads or asyncio help, and one CPU core is enough.
- If it is mostly **computing** (number crunching, image maths, parsing huge text in Python),
  the job is **CPU-bound**. Only more cores help, so in normal (GIL) Python you need
  **processes**.

For each workload below, write:

1. **I/O-bound or CPU-bound** (or "both, in stages").
2. **Threads, processes or asyncio** (or a mix).
3. **One-line reason.**

The workloads:

1. Download 200 web pages and save each to a file.
2. Resize 5,000 photos from 4000×3000 to thumbnails with pure-Python pixel code (or Pillow).
3. Parse a 2 GB log file line by line with regular expressions and count error codes.
4. A chat server that keeps 3,000 users connected at once and forwards their messages.
5. Call a slow weather API for 50 cities, using an old library that only has blocking calls
   (`requests`-style, no `async` version).
6. Check 1,000,000 numbers for being prime with a Python loop.
7. A script that reads one 2 KB config file at start-up, then does nothing else slow.
8. Download 300 PDF files, then extract and count every word in each one (heavy text work).

Write `answer.md`: one short bullet or paragraph per workload (about 250 to 350 words).

**Example of the level of detail expected (a different workload)**

> *"Send 500 emails through an SMTP server."* **I/O-bound**: each send is mostly waiting for
> the server to answer. **asyncio** (with an async SMTP library) or a **thread pool** of about
> 10 workers. Processes would add start-up cost and memory for no gain, because the CPU is idle
> while it waits.
