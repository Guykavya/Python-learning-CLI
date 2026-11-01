## Hint 1

What does each worker do forever, and how does it learn that there is no more work?
`queue.get()` waits when the queue is empty, so "the queue is empty" is not a stop signal: a
worker might just be early. How many stop messages do you need if there are 3 workers and each
stops after taking one?

## Hint 2

```
jobs = Queue(); results = [None] * len(items)

define consumer():
    loop:
        job = jobs.get()
        if job is STOP: break
        index, item = job
        results[index] = work(item)

start n_workers consumer threads
for index, item in enumerate(items): jobs.put((index, item))
repeat n_workers times: jobs.put(STOP)
join all workers; return results
```

Why does `[0, None, "", 3]` still work, even though the sentinel is `None`?
