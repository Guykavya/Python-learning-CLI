## Hint 1

For each exception, walk down the `except` list and ask "is this exception an instance of that
class?". Stop at the first "yes". A `DbTimeout` is a `DbTimeout`, a `DbError` and an `AppError`, so
which clause it lands in depends only on which one comes **first**.

## Hint 2

Make a small table for `handle`:

```
kind      raised         first matching clause    then
timeout   DbTimeout      except DbTimeout         finally
db        DbError        except DbError           finally
net       NetworkError   except AppError          finally
none      nothing        (else)                   finally
value     ValueError     none of them!            finally, then the error leaves handle
```

In `bad_order`, the first clause is `except AppError`. Can the second clause ever run?
