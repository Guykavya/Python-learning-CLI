- Saving the checkpoint before committing the page. A crash in between skips that page forever,
  silently.
- One big transaction for the whole run, committed at the end. The checkpoints then point at
  pages whose rows were rolled back by the crash, and the resume skips them.
- Plain `INSERT`. The page that is replayed after a crash between commit and checkpoint raises
  `IntegrityError` (or creates duplicates without a primary key), so the pipeline can never
  resume.
- `INSERT OR IGNORE` / `DO NOTHING`. Re-runs no longer fail, but a replayed page cannot update
  an order that changed in the meantime.
- Ignoring the checkpoint on start-up ("just run it again"). It works with an upsert, but every
  crash costs the whole extract again; the test counts requests.
- Forgetting to delete the checkpoint at the end. The next scheduled run "resumes" at the last
  page and loads almost nothing, and nobody notices.
- Building cursors yourself (`"offset-6"`) or sending `cursor=None` on the first request. Cursors
  are opaque; send only what the server gave you, and leave the parameter out on page 1.
- Catching the request error to "keep going". The run must stop so that the checkpoint keeps
  pointing at the page that failed.
