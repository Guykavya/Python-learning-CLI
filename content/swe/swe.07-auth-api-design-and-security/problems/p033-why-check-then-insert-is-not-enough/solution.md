## Approach

Think about what is known, and when. After a timeout the client knows nothing, so it must retry; the key lets the *server* recognise the retry. But recognising it requires a **claim** that two requests cannot both make. "Look, then write" is two steps, and between two steps something else can run. The database can do "look and write" as one step, with a unique constraint (an `INSERT` that fails when the key exists).

See `answer.md` for a model answer and a checklist. The key sentences: **a read is not a claim**, and **the effect and its record must succeed or fail together**.

Example timeline of the race, with requests A and B:

```text
A: SELECT -> none        B: SELECT -> none
A: charge(25.00)         B: charge(25.00)            <- both charged
A: INSERT key            B: INSERT key               <- (with a unique constraint B would fail here, but too late)
```

The fixed order is: `INSERT` the key (B fails and replays or answers 409) -> work + "completed" mark in one transaction -> reply.

## Complexity

Not applicable.

## Another way

For operations that are naturally idempotent (`PUT /orders/7/status` to "paid", "set the balance to X", delete by id) no key is needed: doing it twice gives the same state (section 13.2). Use keys for operations that *add* something (payments, orders, e-mails). The same claim-then-act idea protects webhook handlers (dedupe on the event id) and queue consumers (section 13.8).
