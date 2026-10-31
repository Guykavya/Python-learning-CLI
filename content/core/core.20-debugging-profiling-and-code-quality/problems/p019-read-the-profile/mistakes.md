- **Optimising the function with the biggest cumtime.** That is `main` or `<module>`: they only
  contain the work, they do not do it.
- **Reading `percall 0.000` as "free".** It is rounding. Multiply back: 100,000 cheap calls add up.
- **Trusting a guess over the measurement.** `parse` looked suspicious, but it is 11% of the run.
- **Comparing timings between machines.** Use the shares (percent of total) and the call counts;
  the absolute seconds change with the machine and even between runs.
- **Forgetting that the profiler slows everything down.** Code with many small calls runs
  noticeably slower under `cProfile`. Use the profile to find the hot spot, then measure the
  real speed-up with `timeit` or `perf_counter` without the profiler.
- **Making each call faster when you could remove the calls.** The best fix for `find_user` is
  not a faster loop; it is not scanning at all.
