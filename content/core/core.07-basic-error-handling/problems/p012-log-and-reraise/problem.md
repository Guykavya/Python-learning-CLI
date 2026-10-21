# Log it, then let it go

Write `load_score(scores, name, log)` that returns `scores[name]`.

When the name is missing, the function should **record** the problem but **not handle** it:

- append the string `"missing score: <name>"` to the list `log`, then
- re-raise the **same** `KeyError` with a bare `raise` (section 11), so the caller still sees it.

Only a `KeyError` is logged. Any other exception (for example `TypeError` if `name` is a list,
which cannot be a dict key) passes through without touching the log.

**Example**

```python
scores = {"asha": 82}
log = []
load_score(scores, "asha", log)    # 82, log stays []
load_score(scores, "ravi", log)    # raises KeyError: 'ravi'
log                                # ['missing score: ravi']
```
