## Approach

| Case | From -> to | Functions that run |
|---|---|---|
| 1 | 0002 -> head (0004) | `upgrade 0003`, `upgrade 0004` |
| 2 | 0002 -> one step back (0001) | `downgrade 0002` |
| 3 | 0004 -> 0002 | `downgrade 0004`, `downgrade 0003` |
| 4 | base -> 0003 | `upgrade 0001`, `upgrade 0002`, `upgrade 0003` |
| 5 | 0003 -> base | `downgrade 0003`, `downgrade 0002`, `downgrade 0001` |

(Checked by running a four-revision chain with Alembic and logging every call.)

The rule to remember: **`upgrade` runs the revisions' `upgrade()` for each step forward; `downgrade` runs the `downgrade()` of each revision that is being removed**, so to leave the database at revision R you undo only the revisions after R. After case 5 the table `alembic_version` is empty: nothing is applied.

## Complexity

Not applicable.

## Another way

`alembic history` prints the chain and `alembic current` the database's revision; `alembic upgrade --sql` prints the SQL without running it, which is a good way to review a migration.

## Why it matters

Before running a migration on production you must be able to say which steps it will take, and which step undoes it.
