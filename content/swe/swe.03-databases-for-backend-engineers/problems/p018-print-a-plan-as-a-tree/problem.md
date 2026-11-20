# Print a plan as a tree

`EXPLAIN QUERY PLAN` returns rows `(id, parent, notused, detail)`: a **tree** stored as a flat list. A node with `parent == 0` is a root; any other node hangs under the node whose `id` equals its `parent`. Write

```python
plan_tree(rows)
```

returning one string: one line per node, the `detail` text indented by **two spaces per level**, parents before their children, **siblings in order of `id`**, lines joined with `"\n"` and no trailing newline. An empty list gives `""`.

The rows may arrive in any order (do not rely on parents coming first). Do not use recursion (plans can be deep, and it is a good habit): use a stack.

## Example

```python
rows = [(2, 0, 0, "SEARCH orders USING INDEX idx (customer_id=?)"),
        (7, 0, 0, "USE TEMP B-TREE FOR ORDER BY"),
        (9, 2, 0, "CO-ROUTINE sub"),
        (12, 9, 0, "SCAN items")]
print(plan_tree(rows))
```
```text
SEARCH orders USING INDEX idx (customer_id=?)
  CO-ROUTINE sub
    SCAN items
USE TEMP B-TREE FOR ORDER BY
```
