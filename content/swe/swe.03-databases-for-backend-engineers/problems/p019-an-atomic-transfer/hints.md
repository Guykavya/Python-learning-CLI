## Hint 1

What would go wrong if the debit were committed and then the program crashed before the credit? Which statement of Python's `sqlite3` makes a block "all or nothing"?

## Hint 2

`with db:` starts a transaction on the first write and commits at the end, or rolls back if the block raises. So raising an exception **inside** the block undoes the debit.

## Hint 3

```text
validate amount and src != dst (ValueError)
with db:
    UPDATE ... SET balance = balance - ? WHERE id = src AND balance >= ?
    rowcount == 0 -> missing account or not enough money (look which): raise
    UPDATE ... SET balance = balance + ? WHERE id = dst
    rowcount == 0 -> raise LookupError   (the with-block rolls the debit back)
```
