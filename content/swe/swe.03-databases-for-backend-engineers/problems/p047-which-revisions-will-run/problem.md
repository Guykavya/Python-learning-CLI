# Which revisions will run?

Chapter section 13.4. Alembic keeps the chain of revisions

```text
base  ->  0001  ->  0002  ->  0003  ->  0004   (head)
```

and records the **current** revision of each database in its `alembic_version` table. `upgrade X` runs the `upgrade()` of every revision **after** the current one up to and including `X`, oldest first. `downgrade X` runs the `downgrade()` of every revision from the current one **down to but not including** `X`, newest first. `head` is `0004`, `base` is "nothing applied", and `-1` means "one step back from the current revision".

For each case write which functions run, **in order**, as `upgrade 0003` or `downgrade 0002`, separated by commas:

```text
1. current 0002:   alembic upgrade head
2. current 0002:   alembic downgrade -1
3. current 0004:   alembic downgrade 0002
4. empty database: alembic upgrade 0003
5. current 0003:   alembic downgrade base
```

Write your answer in `answer.txt`, one line per case:

```text
1: upgrade 0003, upgrade 0004
```

Do not run it.

## After you answer

1. In case 3, why is `downgrade 0002` not running the `downgrade()` of revision 0002?
2. In case 5, what is in `alembic_version` afterwards?
3. Why must `downgrade()` be written as the exact inverse of `upgrade()`?
