## Approach

| Version | What happens | task_saved | emails_sent | half_saved | outbox_pending |
|---|---|---|---|---|---|
| v1 send, then commit | the provider is down: the exception skips the commit, the rollback drops task and audit | no | 0 | no | 0 |
| v2 commit, then send | the data is committed, then the e-mail fails: the client sees an error and retries, creating a duplicate | yes | 0 | no | 0 |
| v3 send OK, then the process dies before commit | the e-mail **left**, the data is lost: a message about something that never happened | no | 1 | no | 0 |
| v4 the repository commits inside `add` | the task is saved by the first commit; the audit write then fails: a task with no audit line | yes | 0 | **yes** | 0 |
| v5 outbox: task, audit and event in one transaction | all saved together; the e-mail goes later and fails now, so the event **stays pending** and will be retried | yes | 0 | no | 1 |

Reading the table (chapter 9.1 and 9.2): **v1 and v2 are the two classic orders**, and neither is right (a rolled-back change may e-mail, or a saved change may lose its e-mail); **v3 shows the e-mail leaving for a change that was never saved**; **v4 is the answer to "Try it: where does the commit belong?"**: a commit inside the repository means the transaction cannot span several writes, and a failure between them leaves half a change; **v5 is the outbox**: the intention is saved in the same transaction as the change, so a failing provider no longer fails (or loses) anything, at the price of **at-least-once** delivery (a dispatcher that crashes after sending, before marking the row, sends again: the consumer must be idempotent, swe.08).

## Cost

Reading only. The program is small on purpose: run it, then move the `db.commit()` of `v1` to different places and predict the new line before you run it.

## Another way

Combine v5 with a unit of work (p009): the commit belongs to the **use case**, once, at the very end, and the e-mail is a separate step that reads the outbox (p013).
