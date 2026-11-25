# A change log

Chapter section 1.3. Cleaning rule 2 says: **every change must be countable**. "I removed duplicates" is not a log
entry; "I removed 1 row because the whole row was repeated" is. A tiny helper makes the log automatic.

Write two functions.

`log_step(log, name, before, after, note="")`

- `log` is a Python list. Append **one dict** to it with exactly these keys:
  `step` (the `name`), `rows_before` (`len(before)`), `rows_after` (`len(after)`), `dropped` and `note`.
- `dropped` is `rows_before - rows_after`, but **never negative**: a step that adds rows (a merge, say) has `dropped = 0`.
- Return `after`, so steps can be chained: `df = log_step(log, "...", df, df.drop_duplicates())`.
- Do not change `before` or `after`.

`show_log(log)` returns the log as **plain text** (a string, not printed):

- the first line is the header `step | rows_before | rows_after | dropped | note`
- then one line per entry, in order, with the five values joined by `" | "`
- lines are joined with `"\n"`, with no newline at the end; an empty log gives only the header line

## Example

```python
import pandas as pd

raw = pd.DataFrame({"id": [1, 2, 2, 3]})
log = []
df = log_step(log, "load raw", raw, raw, "start")
df = log_step(log, "drop repeats", df, df.drop_duplicates(), "whole row repeated")
print(log[1])
print(show_log(log))
print(show_log([]))
```

```text
{'step': 'drop repeats', 'rows_before': 4, 'rows_after': 3, 'dropped': 1, 'note': 'whole row repeated'}
step | rows_before | rows_after | dropped | note
load raw | 4 | 4 | 0 | start
drop repeats | 4 | 3 | 1 | whole row repeated
step | rows_before | rows_after | dropped | note
```
