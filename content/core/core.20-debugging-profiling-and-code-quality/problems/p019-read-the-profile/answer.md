1. **`tottime`** is the time spent in the function's **own** lines, not counting the functions it
   calls. **`cumtime`** is the total from entering the function until it returns, including
   everything it calls. `build` itself (its loop, the tuple unpacking, the dictionary update)
   took 0.075 s, but during its run it called `parse` (0.063), `find_user` (0.392), `dict.get`
   (0.018) and `list.append`, so its cumulative time is 0.075 + 0.063 + 0.392 + 0.018 ≈ 0.548.

2. `main` does almost nothing itself: it only calls `load`, `build` and `sorted`. A large
   `cumtime` with a tiny `tottime` means "the time is somewhere **below** me". It is the entry
   point, so of course its cumtime is about the whole run. Follow the cumtime downward until you
   reach a function whose **tottime** is large.

3. `find_user` calls no Python functions and no listed built-ins (the `==` comparison and the
   loop happen inside its own code), so all of its time is its own: tottime = cumtime. `percall`
   is rounded to three decimals. The real value is 0.392 / 100000 ≈ **3.9 microseconds** per call,
   tiny for one call but it runs 100,000 times.

4. No. `parse` costs 0.063 s cumulative, about 11% of the run. A ten times faster `parse` would
   save about 0.057 s: the program would go from 0.58 s to about 0.52 s. Optimising the wrong
   function is wasted effort; the profile shows where the time actually goes.

5. Change **`find_user`** (68% of the time, 0.392 s). It scans a list that grows to 400 names for
   every one of 100,000 lines: up to 40 million comparisons. Keep the seen users in a **set** (or
   just check `name in totals`, because the dictionary already knows every user) so each check is
   one hash lookup, O(1). Then the run should drop to roughly the cost of `load`, `parse` and the
   loop, about 0.15 to 0.2 s under the profiler, around three to four times faster. Measure again
   afterwards to confirm; the next hot spot will then be `build` and `parse`.
