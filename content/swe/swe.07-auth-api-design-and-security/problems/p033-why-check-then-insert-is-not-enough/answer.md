## Model answer

**1. The client is blind.** A request can fail in three places: before the server acts, while it acts, or after it acted but before the reply arrives. In the last case the money has moved, yet the client sees only a timeout, exactly as in the first case. It cannot know which one happened. If it gives up, the customer may have paid for nothing; if it retries, the customer may pay twice. Networks, load balancers, queues and double-clicking users retry all the time, so the server must make a retry **safe**.

**2. The key.** The client makes one unique key per *logical payment* (a UUID) and sends it in `Idempotency-Key` on every retry of that payment. The server remembers, per user and key, a fingerprint of the request and the stored response. A repeat with the same key and body does not run the work again: it gets the **same response** back. The same key with a different body is a client bug and is refused (`422`), and a key that is still running gets `409`.

**3. The race.** The code does *check*, then *charge*, then *insert*, in separate steps. Two requests with the same key arrive together. Both run the `SELECT` before either has run the `INSERT`; both see "not found"; both call `charge`. The gap is the time between the check and the insert. Reading is not claiming: nothing stops the second reader.

**4. The crash gap.** If the process dies after `charge(...)` but before the `INSERT`, the money has moved and no key was stored. The retry finds no key and charges again.

**5. The fix.** First, **claim** the key with a single atomic statement, an `INSERT` into a table with `PRIMARY KEY (user_id, key)`. The database's **unique constraint** lets exactly one request win; the loser gets an integrity error and answers from the stored record (replay, `409` or `422`). This turns "check then act" into "act on the claim". Second, the effect and the "completed" mark must go in **one transaction**: either both happen or neither, so a crash leaves nothing behind and a retry is safe. When the effect is outside our database (a card network), a transaction cannot cover it, so we pass our key on as *their* idempotency key. Scope keys to the user, so one customer cannot collide with another.

**Checklist: your answer should mention**
- [ ] the client cannot distinguish "failed" from "succeeded but the reply was lost", so it must retry
- [ ] retrying without a key can charge twice
- [ ] the key is sent by the client on every retry; the server stores it with a fingerprint and the response, and replays the same response
- [ ] the race: two requests both pass the check before either inserts (the gap between `SELECT` and `INSERT`)
- [ ] the crash gap: died after the charge and before the insert, so a retry charges again
- [ ] the fix: claim the key atomically with a **unique constraint** before doing the work
- [ ] the work and the "completed" mark in one **transaction** (or pass the key to the outside system)
- [ ] keys are scoped per user; same key with a different body is refused
