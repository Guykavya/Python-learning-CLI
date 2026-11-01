# Explain: choose the concurrency tool

This is the module's design question. For each of the five systems below, write:

1. **Tool**: threads, processes, asyncio, or a mix (say which part uses which).
2. **Why**: is the work I/O-bound or CPU-bound, and what does that imply (the GIL, the cost of
   a process, how many things wait at once)?
3. **Bounding**: how you limit concurrency (which object, roughly what number, and why that
   number), and where back-pressure comes from if input arrives faster than you can handle it.
4. **Timeouts and cancellation**: what happens when one unit of work hangs or fails, and what
   happens on shutdown (Ctrl+C / deploy).
5. **Why not the others**: one sentence for each tool you did not pick.

The systems:

- **A. Scraper.** Fetch 10,000 product pages from one shop's website, parse each page (a few
  milliseconds of HTML parsing), and save the results. The shop allows about 10 requests per
  second.
- **B. Thumbnailer.** A folder holds 5,000 photos (5 MB each). Make three thumbnail sizes of
  each with a pure-Python image library (no C speed-ups). The machine has 8 cores.
- **C. Telegram bot.** Thousands of users chat with the bot. Each message needs one HTTP call
  to an AI API (2-10 seconds) and one database query. The bot must keep answering other users
  while some calls are slow.
- **D. Log aggregator.** Tail 40 log files on one server as they grow, parse each new line with
  a regular expression, and send batches of parsed lines to a central server every second.
- **E. ML preprocessing + upload.** Turn 200 GB of raw CSV files into feature arrays (heavy
  NumPy-free Python number crunching per row), then upload each result file (about 1 GB) to
  cloud storage.

Write `answer.md`: about 100 to 150 words per system (500 to 750 in total). A table is fine
for the "tool / why" part, but explain bounding and cancellation in sentences.

**Example of the level of detail expected (a different system)**

> *Sending 2,000 welcome emails through an SMTP server.* **asyncio** with an async SMTP client
> (or a thread pool of ~10 if only a sync client exists): the work is pure waiting on the
> network. **Bounding:** an `asyncio.Semaphore(10)`; the mail provider throttles above that.
> **Timeouts:** `asyncio.timeout(30)` per email, two retries with backoff, failures written to
> a "retry later" list; on shutdown the TaskGroup cancels in-flight sends, and the list shows
> what was not sent. **Not processes:** nothing is CPU-bound, and 2,000 processes would cost
> gigabytes. **Not one thread per email:** 2,000 threads for 2,000 sockets is wasteful when one
> event loop can wait on all of them.
