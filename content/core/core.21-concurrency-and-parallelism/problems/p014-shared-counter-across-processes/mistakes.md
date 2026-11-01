- Expecting a global to be shared between processes. Each process has its own copy.
- `counter.value += 1` without `get_lock()`. Processes run truly in parallel, so updates are
  lost; the GIL is per process and protects nothing here.
- `with counter.get_lock(): ...` around the **whole** loop. Correct, but then the processes
  run one after another; usually fine for this exercise, wasteful in real code.
- Creating the `Value` at module level. With spawn/forkserver each child imports the module and
  creates its **own** `Value`, which is not the parent's.
- `Value("i")` without a start value, or reading `counter` instead of `counter.value`.
- Forgetting `join()`. The parent reads the value before the children have finished.
- Lambda or nested function as `target`. With spawn/forkserver it must be importable by name.
