## Model answer

**What goes wrong.** `BackgroundTasks` runs the work **inside the web process**, after the response, and the list of tasks lives only in that process's memory.

- A **deploy or crash** kills the process: tasks that have not finished are simply gone. A 40-second PDF that was half done is never made, and nobody knows. The order exists, the receipt and invoice do not.
- There is **no retry**: if the e-mail provider times out once, the receipt is lost.
- The work **competes** with requests for the same CPU and memory: 50 orders a minute means up to 33 PDFs being built inside the web server, which slows every page. There is no visibility either: no list of pending tasks, no failed ones to inspect.

**What a durable queue adds.** Jobs are stored **outside** the web process (a database table, Redis, RabbitMQ), so they survive restarts; **retries** with backoff; a **dead-letter** state for jobs that keep failing; separate **worker processes** that you can scale and deploy on their own; **visibility** (queue length, oldest job age, errors).

**What goes in the payload.** The order **id** (`{"order_id": 812}`), not the object. (1) The object is a snapshot: if the order is cancelled or edited before the job runs, the worker would act on old data; reading by id gets the current truth. (2) Size and privacy: personal data would sit in the broker, logs and dead letters. Also, an ORM object tied to a request's database session cannot be used after the request ends, and it may not be serialisable to JSON at all.

**When it is fine.** Tiny work that may be lost: writing an analytics log line, updating a "last seen" timestamp.

**What to return.** For slow work: `202 Accepted` with `{"id": 812, "invoice_status_url": "/orders/812/invoice"}`, and the client polls the status (chapter 8.2). Here the order itself is created at once, so `201` with the id is fine, plus the status URL for the invoice.

**Checklist: your answer should mention**
- [ ] tasks live in the web process's memory and are lost on a restart, deploy or crash
- [ ] no retries, no record of failures, no visibility
- [ ] slow work in the web process competes with requests for CPU and memory
- [ ] a durable queue stores jobs outside the process and adds retries, dead letters, separate scalable workers, monitoring
- [ ] the payload carries ids, not objects: current data, small size, no personal data in the broker
- [ ] `BackgroundTasks` is fine for tiny, losable work
- [ ] `202 Accepted` (or 201 for the order) plus a status URL that the client can poll
