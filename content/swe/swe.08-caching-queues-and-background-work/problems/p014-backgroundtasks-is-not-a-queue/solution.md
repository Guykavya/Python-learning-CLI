## Approach

The model answer is in `answer.md`. The key fact is one sentence: **`BackgroundTasks` keeps the work in the memory of the process that answered the request.** Everything else follows: lost on restart, no retries, competes with requests. A queue is a **promise stored somewhere durable** and kept by separate workers.

## Cost

A queue costs a broker (or a table) and worker processes to run and monitor. That is worth it for anything the user would complain about losing: e-mails, invoices, exports, webhooks.

## Another way

For a small project, a database-backed queue (chapter 9) gives durability with no new service: the job row can even be written in the **same transaction** as the order (the outbox, chapter 11.7), so an order never exists without its receipt job.
