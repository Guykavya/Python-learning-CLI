- Fixing the duplicates with `DELETE FROM orders` at the start of every run. A full run looks
  fine, but a resume deletes the pages loaded before the crash and loads only the rest.
- `INSERT OR IGNORE`. No duplicates, but orders that changed on the server keep their old
  values forever.
- `INSERT OR REPLACE` without adding a primary key. Without a key nothing conflicts, so it still
  appends.
- Moving `save_checkpoint` just below `transform`. It passes the `TypeError` incident but still
  loses the page when the database write fails.
- Catching the `TypeError` and skipping the bad order to "make the run finish". The broken order
  is then silently missing, and the checkpoint moves past it. Quarantining bad records is a
  different design decision (with its own file and counts); this job must stop.
- Deleting the checkpoint at the start of the run to "be safe". Every crash then costs a full
  re-run.
- Wrapping the whole run in one transaction. The checkpoint (a file) is saved page by page but
  the rows are only committed at the end, so a crash loses rows the checkpoint claims.
