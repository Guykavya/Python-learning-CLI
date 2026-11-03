## Hint 1

You need to remember, for every id you have seen so far, "the best version so far". Which data
structure maps an id to something? When a new version of an id arrives, there are exactly two
cases: it is older (ignore it), or it is newer **or equally new** (it replaces the stored one).
Why does "equally new" belong to the second case?

## Hint 2

A dict remembers the order in which keys were **first inserted**; assigning a new value to an
existing key does not move it. That gives you "first-seen order" for free.

```
best = {}                                   # id -> (parsed time, record)
for record in records:
    t = datetime.fromisoformat(record["updated_at"])
    if record["id"] not in best or t >= best[record["id"]][0]:
        best[record["id"]] = (t, record)
return [record for each (t, record) in best.values()]
```
