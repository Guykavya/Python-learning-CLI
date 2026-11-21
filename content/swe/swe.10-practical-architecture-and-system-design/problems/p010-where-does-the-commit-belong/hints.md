## Hint 1

For each version write two columns while you read the code from top to bottom: **committed** (what `saved` holds) and **left the building** (e-mails sent). Mark the line where the failure happens and apply what the `except` does: everything not yet committed is dropped.

## Hint 2

`half_saved` is `yes` only when `tasks` and `audit` in `saved` differ. `outbox_pending` is how many outbox rows were committed (the dispatcher has not delivered them: in `v5` its attempt fails). In `v4` the first commit already saved the task; the `IOError` comes before the audit insert, so what is saved?
