## Hint 1

Where does `count` live after `Process.start()`? With the default start methods the child is
a fresh Python that **imports** your module, so it gets its own `count = 0`. How could the
parent and the children point at the **same** piece of memory? What do you pass to the child
so it can reach it?

## Hint 2

```
add_many(counter, times):
    repeat times:
        with counter.get_lock():
            counter.value += 1

count_in_processes(n_procs, per_proc):
    counter = Value("i", 0)
    procs = [Process(target=add_many, args=(counter, per_proc)) ...]
    start all, join all
    return counter.value
```

Why must the `Value` be created inside `count_in_processes` and passed in `args`, not created
at module level?
