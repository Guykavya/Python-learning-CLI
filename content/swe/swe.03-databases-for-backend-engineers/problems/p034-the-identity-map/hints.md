## Hint 1

`Session.get(Customer, 1)` first looks in the identity map. If the object is there (and not expired) it is returned with no SQL.

## Hint 2

Step 3 uses another session with its own empty map: a query, and a different object. Step 4: `expire(a)` itself does not touch the database; reading `a.name` afterwards does (one `SELECT`).

## Hint 3

Step 5: `commit()` expires all objects, then `a.name` reloads `a` (one query). Step 6: `get` finds `a` in the map, already refreshed by step 5: no query, and it is the same object.
