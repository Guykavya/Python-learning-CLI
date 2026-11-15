## Hint 1

Do not write `run_pipeline` first. Build and test the parts that need no network:
`transform` (run the `test_transform_*` tests), then `save_checkpoint` / `load_checkpoint`, then
`export_partition` on a small SQLite table you fill by hand. Only then write the loop. For the
loop, draw the timeline of one page on paper: *fetch -> transform -> write to SQLite -> commit ->
save checkpoint*. For each arrow, ask: if the process dies exactly here, what does the next run
see in SQLite and in the checkpoint, and does it end up with the same result as a clean run?

## Hint 2

Three rules make every crash harmless:

1. **Data before checkpoint.** A crash between them repeats one page; the upsert makes the repeat
   harmless (rows are `unchanged`, the quarantine uses `INSERT OR IGNORE`).
2. **Watermark last.** Commit it only after every partition is exported, so a crash in the export
   is resumed (with `fetch_done = True` and zero requests), not forgotten.
3. **Days from every good record**, not only from changed rows, so a repeated page still exports
   its days.

```
state = load_checkpoint(path) or {"since": committed watermark, "cursor": None, "max_updated_at": None,
                                  "days": [], "fetch_done": False, "run_id": run_id}
while not state["fetch_done"]:
    if pages == max_pages: raise RuntimeError
    page = fetch_page(params from state)                 # retries inside
    with conn:                                           # one transaction per page
        for record in page["items"]:
            try: row = transform(record, secret)
            except BadRecord as e: quarantine (INSERT OR IGNORE) + log warning; continue
            outcome = upsert_if_newer(row); days.add(day); track max updated_at
    state = {...state, cursor: next_cursor, days, max_updated_at, fetch_done: next_cursor is None}
    save_checkpoint(path, state)                         # AFTER the commit
for day in sorted(days): export_partition(conn, root, day)
commit watermark = max(old, max_updated_at); delete checkpoint; log summary; return summary
```
