## Hint 1

If you call `store(obj)` and do not assign its result, what happens to the list it built as
soon as the call returns? And why does the problem insist on `object()` instead of, say, `7`?
What would `sys.getrefcount(7)` show on Python 3.12+?

## Hint 2

```
obj = object()
before = sys.getrefcount(obj)
kept = store(obj)          # keep the container alive!
after = sys.getrefcount(obj)
return after - before
```
