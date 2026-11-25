- **A module-level `LOG = []` inside your solution.** The chapter used a global for brevity, but then two pipelines
  share one log and a second run appends to the first. Here the log is an argument: the caller owns it.
- **Forgetting `return after`.** The next line of the pipeline gets `None` and crashes with a confusing error.
- **`dropped = rows_before - rows_after` without `max(0, ...)`.** A step that adds rows shows "dropped -3", which is
  nonsense in a report.
- **Printing instead of returning from `show_log`.** The caller cannot store or test a printed text.
- **A trailing newline, or a missing header on an empty log.** The format is part of the contract.
