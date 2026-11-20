## Approach

| # | Scenario | Worker-1 | Worker-2 | Result |
|---|---|---|---|---|
| 1 | crash at start | dies before sending | sends, acks | (1, 0) |
| 2 | crash before send | dies before sending | sends, acks | (1, 0) |
| 3 | crash after send | sent (1), dies | sends again (2), acks | (2, 0) |
| 4 | crash at end | sent (1), dies before the ack | sends again (2) | (2, 0) |
| 5 | response lost | sent (1), `TimeoutError` -> not acked | sends again (2) | (2, 0) |
| 6 | two jobs, no crash | job 1 (1), job 2 (2) | nothing left | (2, 0) |
| 7 | two jobs + crash after send | job 1 sent (1), dies | job 1 again (2), job 2 (3) | (3, 0) |

The second number is always 0: at-least-once never **loses** a job. The danger window is "after the effect, before the ack" (lines 3, 4 and 5), plus duplicate jobs (6 and 7), which no crash is needed for.

## Cost

Reading only. This table is the argument for every defence in p022: a log of sent keys covers a duplicate after the record; a provider idempotency key covers the window between send and record and the lost response; a business key (not the job id) covers two jobs for one e-mail.

## Another way

Rewrite `naive_handler` with a `sent_keys` set and a key `f"welcome:{job['to']}"` passed to a `send` that ignores repeated keys, and run all seven lines again: every line becomes `(1, 0)`.
