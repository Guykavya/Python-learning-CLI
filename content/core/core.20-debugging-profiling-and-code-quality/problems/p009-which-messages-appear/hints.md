## Hint 1

For each call, first find the **effective level** of the logger (`db` has none of its own, so
it uses `app`'s; `other` has none, so it uses the root's). Is the message at or above it? Then
list the handlers the record visits: its own, then its parent's, then the root's (unless
`propagate` is `False`). Check each handler's level only.

## Hint 2

Make a small table:

```
logger   effective level   handlers visited (handler level)
app      INFO              app(DEBUG), root(WARNING)
app.db   INFO (from app)   app(DEBUG), root(WARNING)
app.web  DEBUG             web(ERROR)            -- propagate False
other    ERROR (from root) root(WARNING)
```

The root logger's own level is `ERROR`, but a `WARNING` that **propagates** into the root's
handler is still printed. Why?
