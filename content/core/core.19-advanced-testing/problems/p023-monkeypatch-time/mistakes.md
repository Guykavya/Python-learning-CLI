- `from time import monotonic` in the module: patching `time.monotonic` later changes nothing, because
  the module keeps its own reference (patch the name where it is used).
- Recording rejected calls: a flood of refused calls would keep the limiter blocked forever.
- `<=` at the border: the slot frees exactly when `now - t >= per_seconds`.
- Calling `now()` several times in one `allow`: a fake clock that returns a list of values runs out.
- Using `time.time()`: it can jump backwards (clock changes); durations should use `monotonic`.
