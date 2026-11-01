- `pool.map(lambda r: sum(i * i for i in r), chunks)`: lambdas cannot be pickled, so the
  workers cannot receive them (`PicklingError`).
- Defining the worker inside `parallel_sum_squares`. Same problem: it has no importable name.
- Sending `list(range(...))` chunks. It works, but pickling a million ints is slow; a `range`
  pickles to three numbers.
- Chunks computed with `n // k` only, so the last `n % k` items are never summed.
- Creating one pool per chunk. Every pool starts new processes; create one pool and reuse it.
- Running the script without `if __name__ == "__main__":` on Windows/macOS: each worker imports
  the file and starts the pool again (Python stops this with a `RuntimeError`).
- Expecting a speed-up for small `n`. Starting processes costs more than summing a few thousand
  numbers.
