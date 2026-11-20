## Hint 1

What would you like to undo when the second `a@x.com` fails: the whole session, or only that user? Which database feature undoes "only the last part" of a transaction?

## Hint 2

`session.begin_nested()` creates a **savepoint**; leaving its `with` block normally releases it (and flushes), and an exception inside rolls back to the savepoint only. Where does `IntegrityError` appear: at the `add`, or when the block ends (at the flush)?

## Hint 3

```text
for email in emails:
    try:
        with session.begin_nested():
            session.add(User(email=email))
        added += 1
    except IntegrityError:
        skipped.append(email)
session.commit()
```
