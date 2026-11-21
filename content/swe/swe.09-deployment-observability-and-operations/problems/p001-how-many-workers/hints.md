## Hint 1

Two limits apply to the number of workers: a limit from the CPU (the rule of thumb) and a limit from memory. Which of the two would you take if they disagree? What does `memory_mb // mb_per_worker` tell you?

## Hint 2

```text
validate (cpus, mb_per_worker, app_kind, memory_mb >= mb_per_worker)
by_memory = memory_mb // mb_per_worker
if async:   workers = min(cpus, by_memory); threads = None; concurrent = None
else:       workers = min(2*cpus + 1, by_memory); threads = 1 (sync) or 4 (threaded)
            concurrent = workers * threads
```
