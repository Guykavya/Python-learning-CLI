## Approach

| Step | Migration effect | Healthy? | Live | Schema | Does the live version work? |
|---|---|---|---|---|---|
| 1 | none | yes | 1.0 | item, quantity | yes |
| 2 | **adds** `note` | yes | 1.1 | item, note, quantity | yes |
| 3 | **renames** `quantity` to `qty` | no, so the pointer stays on 1.1 | 1.1 | item, note, qty | **NO**: 1.1 needs `quantity` |
| 4 | none | yes | 1.2.1 | item, note, qty | yes |
| 5 | **adds** `tag` | no, so the pointer stays on 1.2.1 | 1.2.1 | item, note, qty, tag | yes: 1.2.1 needs only item and qty |

Step 3: the automatic rollback restored the **code** but the **migration had already run**, so the old code meets a schema without its `quantity` column: errors on every request. The only way out is to **roll forward** to a version that works with the new schema (step 4, the fix 1.2.1), or to restore the database from a backup and accept the loss of the data written since (chapter "Try it: roll forward or back?"). Step 5 shows the safe case: an **additive** migration leaves the old version intact, so rolling back is a real undo.

How to write release 1.2 safely (expand and contract, chapter 12.4): release A adds a nullable `qty` column and code that writes both columns and reads `qty`; back-fill; release B stops using `quantity`; only a later release C drops it, when nobody can need a rollback that far. Each release can then be rolled back alone.

## Cost

Reading only; the cost of ignoring it is the second, longer outage after a "successful" rollback.

## Another way

Run the program and change step 3 to healthy: the service now works (1.2 needs `qty`), but the previous version 1.1 can no longer be rolled back to, which is the quieter form of the same trap: a deployment that cannot be undone.
