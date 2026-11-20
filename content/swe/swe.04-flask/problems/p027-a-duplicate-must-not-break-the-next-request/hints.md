## Hint 1

What state is the session in after `commit()` raised? What does the error message say when you use it again? Read the name of the exception.

## Hint 2

The cure is one call, in the `except` branch, **before** any other use of `db.session`. It discards the failed transaction and gives you a clean session. It is not enough to "let the request end": sometimes the session lives longer than the request.

## Hint 3

```text
try:
    db.session.commit()
except IntegrityError:
    db.session.rollback()          # first!
    ... now query for the suggestions ...
    return 409
```
