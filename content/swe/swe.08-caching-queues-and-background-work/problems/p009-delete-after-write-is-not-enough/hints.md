## Hint 1

First write the six orders. Positions 0 to 3; the reader takes the two positions listed, the writer takes the other two. For `(0, 3)`: position 0 = `r_read_db`, 1 = `w_update`, 2 = `w_delete`, 3 = `r_store`.

## Hint 2

For each order keep three things on paper: `db`, the reader's local `v`, and the cache. The reader's `v` is whatever `db` was **when `r_read_db` ran**. The only way to end stale is that the reader stores an old `v` **after** the writer already deleted.

```text
order (0,3): read v=OLD | db=NEW | cache delete (empty) | store OLD  -> cache=OLD, read=OLD (stale)
```
