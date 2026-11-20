## Hint 1

For each line, follow the two workers separately. Write down, for worker-1: which job it is on, where it stops (crash, ordinary error, or success), and whether `send` already ran. Then do the same for worker-2 with what is still in `pending`.

## Hint 2

The rule: a job is removed from `pending` only when the handler **returns**. So any crash or error **after** `send` means the job runs again, and the naive handler sends again. A crash **before** `send` costs nothing.

```text
line 7: worker-1: job 1 sends (1), crashes after-send -> break
        worker-2: job 1 sends (2), ack; job 2 sends (3), ack   -> (3, 0)
```
