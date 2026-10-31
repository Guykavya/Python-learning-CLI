- **Averaging the batches.** One batch hit by the garbage collector or another program drags the
  mean up. The minimum is the least disturbed run.
- **Forgetting to divide by `number`.** Then the answer is the time of the whole batch, and it
  changes when you change `number`, which makes results impossible to compare.
- **Reading the clock around every call.** The clock costs about as much as a tiny function, so
  you end up timing the clock.
- **Calling `time.perf_counter()` directly instead of `timer()`.** The function then ignores the
  fake clock the tests pass in. Always use the parameter you were given.
- **Using `time.time()` for benchmarks.** It is the wall clock: it can jump when the system
  clock is adjusted and has a coarser resolution on some systems. `perf_counter` is made for
  measuring intervals.
- **Accepting `number=0`.** That divides by zero (or returns nothing useful). Reject bad
  arguments up front with a `ValueError`.
