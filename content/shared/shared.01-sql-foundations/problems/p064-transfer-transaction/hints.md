## Hint 1

Which Python construct commits on success and rolls back when an exception leaves the block? Where must your `raise` statements be, inside it or outside it, if a raise has to undo earlier changes?

What does `cursor.rowcount` tell you after an `UPDATE` that matched no row?

## Hint 2

```
def transfer(con, source, target, amount):
    validate amount and source != target -> ValueError
    with con:
        read source balance (fetchone) -> None means KeyError(source)
        if balance < amount: raise ValueError
        UPDATE ... SET balance = balance - ? WHERE id = ?
        UPDATE ... SET balance = balance + ? WHERE id = ?   -> rowcount == 0 means KeyError(target)
```

The target check happens *after* the debit on purpose: a rollback must be able to undo it.
