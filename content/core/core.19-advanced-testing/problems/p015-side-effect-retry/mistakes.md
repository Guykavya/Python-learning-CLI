- Using `return_value` for failures: a mock cannot return an exception into a `try` block; use
  `side_effect`.
- All errors with the same message, so "raised the first error" and "raised the last error" look
  identical. Give each its own text and use `match=`.
- Never reading `call_count`. Retry bugs are mostly about **how many** calls, not about results.
- A list with fewer items than the code asks for: the mock then raises `StopIteration`, which looks
  like a bug in your test, not in the code.
- Forgetting the "other error" case: catching too much (`except Exception`) is the most common retry bug.
