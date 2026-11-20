## Hint 1

What must the server remember per `(user, key)`? (A fingerprint of the body, a status "in progress" or "completed", and the finished response.) Which of the six situations of the table does a *new* key meet, and which do the others meet? Draw the table on paper before you write code.

## Hint 2

The decision "is this key new?" and the marking "it is mine now" must be one step. Which tool gives you that for a dictionary in memory? Why must the lock be released *before* `provider.charge(...)` and taken again afterwards? What would the second request see if you held it the whole time?

## Hint 3

```text
create(user, key, body):
    fp = fingerprint(body)
    with lock:
        rec = records.get((user, key))
        if rec is None: records[(user, key)] = {fp, "in_progress", None}   # claim; fall through
        elif rec.fp != fp: return 422
        elif rec.status == "completed": return stored response, replayed=True
        else: return 409
    try: charge_id = provider.charge(user, amount)         # NO lock held here
    except ProviderError: with lock: delete record; return 502
    except BaseException: with lock: delete record; raise
    with lock: record = completed with the 201 response
    return 201, response, False
```
