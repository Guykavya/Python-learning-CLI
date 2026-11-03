- Taking the watermark from the last record received. The API's order is by id, not by time, so
  the watermark ends up too low and the next run re-loads data that has not changed.
- Sending `updated_since=None` on the first run. httpx turns it into `updated_since=` (an empty
  string), which a real API may reject or treat as "since the beginning of time" by accident.
  Leave the key out.
- Committing after each page. If page 3 fails, pages 1-2 and possibly a watermark are already
  saved; the run is half done and the state says otherwise.
- Storing the watermark first and loading the data afterwards. A crash in between skips data
  forever: the watermark says it is loaded, the API never sends it again.
- Keeping the watermark in a Python variable or a global. A new process (tomorrow's run) starts
  from scratch. State must be persisted and committed.
- Writing `now()` as the watermark instead of the largest `updated_at` seen. Your clock and the
  server's clock differ, and rows committed on the server during your run are skipped.
- Using plain `INSERT` for the orders. A changed order then fails on the primary key (or is
  duplicated without one). Incremental loads deliver changes, so the write must be an upsert.
- Storing an empty-string or `None` watermark when nothing was received. The next run then
  sends a bad parameter.
