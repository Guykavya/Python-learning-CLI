## Hint 1

`cProfile.Profile()` has `enable()` and `disable()`. Where must `disable()` go so that it runs
even when `fn` raises? Once you have the profiler, `pstats.Stats(profiler).stats` is a plain
dictionary: print it once for a tiny function to see what the keys and values look like.

## Hint 2

Loop over the items of the stats dictionary. Unpack the key into `filename, line, name` and the
value's first two items into `primitive, total`. Skip built-ins and add `total` to `counts[name]`.

```
profiler = cProfile.Profile()
profiler.enable()
try:
    fn(*args, **kwargs)
finally:
    profiler.disable()
counts = {}
for (filename, line, name), (cc, nc, *rest) in Stats(profiler).stats.items():
    if filename == "~": skip
    counts[name] = counts.get(name, 0) + nc
return counts
```
