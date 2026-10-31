- **Running setup once per call of stmt.** Setup runs once per *timing*, before the loop. That
  is why it is the right place for building test data: its cost is not measured.
- **Thinking `repeat()` runs setup once.** It runs one full timing per repeat, each with its own
  setup.
- **Thinking `number=0` skips setup.** The timing still happens, just with an empty loop.
- **Forgetting that the counters are never reset.** `log` lives at module level, so every line
  prints running totals.
- **Expecting the string statement to see `data` without `globals=`.** Without it the string runs
  in a fresh namespace and raises `NameError`.
- **Assuming the garbage collector is on during timing.** `timeit` turns it off so that a random
  collection does not disturb one batch. Code that creates lots of cyclic garbage can look faster
  under `timeit` than in real life; add `gc.enable()` to the setup when that matters.
