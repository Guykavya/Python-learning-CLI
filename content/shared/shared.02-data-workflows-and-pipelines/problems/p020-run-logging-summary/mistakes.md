- Logging the record (`"skipped %r", record`). The customer's email is now in the logs, which are
  kept longer and read by more people than the database.
- `print(...)` instead of the logger. Prints cannot be filtered by level, have no timestamps and
  are lost when the job runs under a scheduler.
- `logging.info(...)` (the root logger) or `logging.getLogger(__name__)` when the problem says
  `"pipeline"`. Operators configure levels and handlers by logger name.
- An INFO line per record. A million-record run writes a million lines; the one summary line
  that matters drowns.
- Forgetting the run id in some lines, so the warnings of two runs cannot be told apart.
- Calling `logging.basicConfig()` inside the function. It changes the logging setup of the whole
  program that imported you.
- `isinstance(id_, int)` alone: `True` passes as an id of 1.
- Logging "finished" in a `finally` block. A failed run would then claim it finished.
- f-strings in log calls work, but they format the message even when the level is disabled;
  `%s` arguments are formatted only when the line is really written.
