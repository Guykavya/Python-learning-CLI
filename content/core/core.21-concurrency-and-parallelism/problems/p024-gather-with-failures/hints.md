## Hint 1

Plain `await asyncio.gather(...)` raises the **first** exception and you lose every other
result. What does `return_exceptions=True` put in the result list instead of raising?

## Hint 2

With `return_exceptions=True`, the list has one entry per id, in order: either a value or an
exception **object**. Walk the ids and the results side by side.

```
results = await gather(*(fetch(i) for i in ids), return_exceptions=True)
ok, failed = {}, {}
for id, r in zip(ids, results):
    if r is an exception:  failed[id] = type(r).__name__
    else:                  ok[id] = r
return ok, failed
```

Why check "is an exception" with `isinstance` rather than "is falsy"?
