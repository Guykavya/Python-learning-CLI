## Hint 1

Level 0 of the index is `store`, level 1 (the innermost) is `channel`. `unstack()` with no argument moves the innermost
level to the columns. What is left on the rows?

## Hint 2

```text
u  = unstack()  : rows = stores  (S1, S2, S3), columns = channels (online, store)  -> (3, 2)
u0 = unstack(0) : rows = channels (online, store), columns = stores (S1, S2, S3)   -> (2, 3)
u.loc["S2"]     : S2's row = [online, store] values
u0.loc["store"] : the "store" channel row = one value per store
u.stack()       : back to 6 values, index levels store, channel, in row order
gap             : S3 has only "online" -> its "store" cell is NaN
```
