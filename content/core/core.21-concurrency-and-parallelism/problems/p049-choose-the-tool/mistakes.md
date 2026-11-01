- Choosing threads for the thumbnailer "because there are many files". The number of items
  does not decide; the **kind of work** does. Pure-Python CPU work on threads uses one core.
- Choosing processes for the scraper or the bot "for speed". They wait on the network; a
  process per request costs memory and start-up time and gains nothing.
- "Use asyncio for everything." An async function that crunches numbers for 2 s freezes every
  other task for 2 s. CPU work goes to an executor.
- Giving no number for the limit, or a number with no reason. The limit comes from the
  bottleneck: the shop's rate, the cores, the API's quota, the bandwidth.
- Confusing **rate** with **concurrency**: `Semaphore(10)` allows 10 in flight, which can be
  hundreds per second if responses are fast.
- Unbounded queues between stages. A slow uploader then lets the fast stage fill memory or disk.
- Retrying everything, including 404s and corrupt files, or not retrying at all.
- Forgetting shutdown: no cancellation, no cleanup, half-written files that look complete.
- Sending big data (5 MB images, 1 GB arrays) to worker processes by pickling instead of
  passing file paths.
