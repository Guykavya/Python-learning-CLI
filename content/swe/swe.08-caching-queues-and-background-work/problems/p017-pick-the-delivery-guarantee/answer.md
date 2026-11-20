## Model answer

**The two guarantees.**

| Ack timing | Crash before the effect | Crash after the effect (before the ack) |
|---|---|---|
| ack first (at-most-once) | **lost**: the broker forgot the job, nothing happened | ok |
| ack after the work (at-least-once) | ok: the job comes back and runs | **duplicate**: the job comes back and the effect happens twice |

At-most-once can **lose** a job; at-least-once can **duplicate** it. Most serious systems choose at-least-once, because a lost invoice or payment is usually worse than a repeat that you can make harmless.

**Why not exactly-once.** The worker cannot do "send the e-mail" and "tell the broker" in one atomic step: they are two different systems, so one always happens first, and the process can die between them. What you build instead is **effectively once**: at-least-once delivery **plus** an **idempotent** handler, so a second run changes nothing. The handler needs (1) a stable business key for the effect (`welcome:7`, `charge:order-812`) and (2) a way to remember or check it: a dedupe record in your database in the same transaction as the effect, or an **idempotency key** sent to the outside provider, which refuses to repeat.

**Why jobs run twice anyway.** A worker crashed or was killed by a deploy after the effect but before the ack; the **lease** expired while a slow worker was still working, so a second worker took the job; the ack was lost on the network; the producer retried the enqueue after a timeout; an operator redrove dead jobs; a broker failover redelivered messages.

**Choices.**

- (a) Page views: **at-most-once** is fine. Losing one count in a million does not matter, and duplicates would inflate the numbers. (Or at-least-once with a dedupe key per event, if exact numbers matter.)
- (b) Card charge: **at-least-once + idempotency key** to the payment provider (`charge:order-812`), plus a unique `(order_id, kind)` row. Only effectively once is acceptable for money.
- (c) Password reset: **at-least-once**. A lost e-mail makes the user try again; a duplicate is mildly annoying and harmless (a new token replaces the old one). An idempotency key per request is a nice extra.
- (d) Delete old sessions: **at-least-once**; the job is **naturally idempotent** (deleting what is already deleted changes nothing), so no extra work is needed. Give it a dedupe key per night so overlapping schedulers do not run it twice at once.

**Checklist: your answer should mention**
- [ ] ack before the work = at-most-once: a crash before the effect loses the job
- [ ] ack after the work = at-least-once: a crash after the effect duplicates it
- [ ] exactly-once delivery is impossible between two independent systems (the effect and the ack cannot be one atomic step)
- [ ] effectively once = at-least-once + idempotent handler (business key + dedupe record or provider idempotency key)
- [ ] at least four causes of duplicates: crash before ack, lease expiry with a slow worker, lost ack, producer retry, redrive, failover
- [ ] (a) at-most-once acceptable; (b) at-least-once + idempotency key; (c) at-least-once; (d) at-least-once, naturally idempotent
