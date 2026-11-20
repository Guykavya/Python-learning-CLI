## Hint 1

For each endpoint ask two questions. Where does it run: an `async def` runs **on the event-loop thread**; a plain `def` endpoint is sent by FastAPI to a **worker thread**. And while it waits, can anything else run: only if the waiting is an `await`.

## Hint 2

`time.sleep` does not `await`: it holds the thread. On the event-loop thread that freezes every other request. FastAPI only looks at the **endpoint** to decide where it runs; a plain `def` helper called from an `async def` endpoint runs right there, on the loop.

## Hint 3

```text
/one    async def + time.sleep        -> loop frozen, 3 x 0.3 s        -> one-at-a-time main
/two    def + time.sleep              -> 3 worker threads in parallel  -> together worker
/three  async def + await sleep       -> loop free during each await   -> together main
/four   async def + helper(time.sleep)-> same as /one                  -> one-at-a-time main
```
