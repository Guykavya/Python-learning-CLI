- "Lambdas can't be pickled because they are anonymous, so give it a name with
  `double = lambda x: x * 2`." The function's `__qualname__` is still `<lambda>`, so it still
  fails. Use `def`.
- Forgetting that **results** and **exceptions** also cross the boundary. A worker that returns a
  generator or raises an exception that cannot be pickled breaks too.
- Thinking the guard is only needed on Windows. With forkserver (Linux, 3.14) and spawn (macOS)
  it is needed too.
- Saying `fork` is the default on Linux. It was until 3.13; 3.14 changed it to `forkserver`.
- Using processes for many tiny tasks. Pickling and start-up can cost more than the work.
- Passing open files, locks or DB connections to workers. Pass paths and settings; let each
  worker open its own.
