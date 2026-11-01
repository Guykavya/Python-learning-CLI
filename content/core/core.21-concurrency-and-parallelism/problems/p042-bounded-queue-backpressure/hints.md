## Hint 1

Three roles: one producer task that walks `items` and puts each into the queue, `n_consumers`
tasks that take from it, and you, waiting for all of them. Which call makes the producer wait
when the queue is full: `put` or `put_nowait`? And how does a consumer that is waiting on
`await queue.get()` ever learn that there will be no more items?

## Hint 2

Results arrive out of order, so carry the position with the item: put `(index, item)` and store
`results[index]`. To stop the consumers, the producer puts one special "done" object per
consumer after the last item; a consumer that gets it returns.

```
DONE = object()
queue = asyncio.Queue(maxsize=maxsize)

producer: for i, item in enumerate(items): await queue.put((i, item))
          repeat n_consumers times: await queue.put(DONE)
consumer: loop: entry = await queue.get()
                if entry is DONE: return
                i, item = entry; results[i] = await consume(item)

async with TaskGroup: start producer + n consumers
return [results[i] for i in range(len(results))]
```
