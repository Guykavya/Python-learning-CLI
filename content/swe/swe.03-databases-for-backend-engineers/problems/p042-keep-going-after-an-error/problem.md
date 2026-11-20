# Keep going after an error

Chapter section 11.4. When a flush fails (for example a `UNIQUE` violation), the session's transaction is **rolled back** and the session cannot be used until you call `session.rollback()`: any further statement raises `PendingRollbackError` ("This Session's transaction has been rolled back due to a previous exception during flush").

`solution.py` has the model `User(id, email)` with a **unique** e-mail. Write

```python
add_users(session, emails)       # -> (added_count, skipped_list)
```

that adds a user for every address in `emails`, but **skips** an address that is already in the database **or** appears earlier in the list:

- add each user inside **`with session.begin_nested():`** (a savepoint); on `IntegrityError` only that user is undone and the address goes to the `skipped` list (in order);
- the earlier good users and the session itself must stay **usable** (no rollback of the whole session);
- finish with `session.commit()` and return `(added_count, skipped_list)`.

## Example

```python
add_users(session, ["a@x.com", "b@x.com", "a@x.com", "c@x.com"])    # (3, ["a@x.com"])
```
