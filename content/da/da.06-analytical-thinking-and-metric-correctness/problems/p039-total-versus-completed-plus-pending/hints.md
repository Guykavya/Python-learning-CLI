## Hint 1

Write the three populations as three boolean masks over the table first: which timestamp and which status does each one
use? Which jobs are in `T` but not in `C`, and which in `C` but not in `T`? What is the reason for each one, and which
fact of the job (status, start date) decides it? Which order must the bridge lines have?

## Hint 2

```text
created = created_at in [start, end);  started = started_at in [start, end)       (NaT is False)
T = created;  C = started and status == completed;  P = started and status == pending
for job in T and not C:  label from the status (cancelled / failed / pending), else "started after the month"
for job in C and not T:  label "created before the month, started in it"
count the labels; steps = T-only labels sorted, each as ("created in month, <label>", -count),
                  then (late label, +count) last;  closes = len(T) + sum(changes) == len(C)
```
