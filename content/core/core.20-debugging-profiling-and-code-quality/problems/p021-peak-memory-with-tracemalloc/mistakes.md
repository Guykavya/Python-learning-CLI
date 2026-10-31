- **Using `current` instead of `peak`.** A function that frees its big list before returning
  ends with almost nothing in use; the peak is the honest number.
- **Not subtracting the starting level.** When tracing was already on, memory allocated before
  the call is part of `current` and would be blamed on `fn`.
- **Forgetting `reset_peak()`.** If someone else started tracing, the peak may come from their
  earlier work.
- **Always calling `stop()`.** It also throws away the other user's data. Stop only what you
  started.
- **No `finally`.** An exception leaves tracing on, and every allocation afterwards is slower.
- **Trusting `sys.getsizeof` instead.** `sys.getsizeof(a_list)` counts only the list's array of
  pointers, not the objects inside it. `tracemalloc` sees every allocation.
