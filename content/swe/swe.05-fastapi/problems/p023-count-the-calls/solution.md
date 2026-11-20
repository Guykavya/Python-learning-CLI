## Approach

Resolve each endpoint's parameters left to right, leaves first, with a fresh cache per request.

```text
/a get_db=1 get_user=1 get_repo=1 endpoint=1
/a get_db=1 get_user=1 get_repo=1 endpoint=1
/b get_db=2 get_user=1 get_fresh_repo=1 endpoint=1
/c get_db=3 get_user=1 endpoint=1
/d get_db=1 get_user=2 endpoint=1
```

- **`/a`.** `user` needs `get_user`, which needs `get_db`: `get_db` runs (1), then `get_user` (1). `repo` needs `get_repo`, whose `get_db` is already cached, so only `get_repo` runs. The endpoint's own `db` is cached too. This is the chapter's point: one `get_db` per request, shared by everyone who asks.
- **Second `/a`.** The cache belongs to a request. A new request starts empty, so the counts are the same again (the chapter's "Try it" shows the total going from 1 to 2).
- **`/b`.** `get_db` runs for `get_user` (1). `get_fresh_repo` asks with `use_cache=False`, so `get_db` runs again (2). The endpoint's `db` is a normal `Depends(get_db)`: a cached value exists, so no third run.
- **`/c`.** `db` runs `get_db` (1). `db2` and `db3` both say `use_cache=False`: two more runs (2, 3). `get_user`'s `get_db` uses the cache. `get_db` is first in the dict because it ran first.
- **`/d`.** `user`: `get_db` (1), `get_user` (1). `again` uses `use_cache=False` on **`get_user`**, so `get_user` runs a second time (2); but inside it, `Depends(get_db)` is cached, so `get_db` stays at 1.

Real output of the program, run with FastAPI 0.162.0 and Pydantic 2.14.3.

## Complexity

Not applicable; this is a reading exercise. (Each dependency runs at most once per request unless `use_cache=False` says otherwise.)

## Another way

Instead of counting by hand, put a `print` in each dependency and run the request once: the print order is the resolution order. The counter dict is the same idea, collected per request.
