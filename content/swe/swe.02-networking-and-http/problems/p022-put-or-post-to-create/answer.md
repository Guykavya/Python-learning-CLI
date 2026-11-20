## Model answer

1. **Who chooses the id.** With `POST /books` the **server** chooses it (and tells the client in the `Location` header). With `PUT /books/42` the **client** chooses it (for example a UUID), and the URL names the resource that must exist after the call.
2. **A retry after a lost reply.** With `POST` the first request created book 42; the retry creates a **second** book (43) with the same content: a duplicate, because the server cannot know that this is the same attempt. With `PUT /books/42` the retry sets book 42 to the same content again: the server answers `200` instead of `201`, but the state is the same: no duplicate.
3. **Idempotent.** An idempotent method has the same effect on the server whether it is applied once or many times. `PUT` means "make this resource look like this": doing it twice gives the same result. `POST /books` means "add a new thing": doing it twice adds two.
4. **Idempotency key.** The client creates a random key (a UUID) **once** per logical operation and sends it as `Idempotency-Key: <uuid>` on the first try and on every retry. The server stores the key together with the response it produced. When the same key arrives again, the server **does not repeat the work**; it returns the saved response (often with a header such as `Idempotent-Replay: true`). So retries cannot create duplicates.
5. **When `POST` is still right.** When the server must choose the id (a database sequence), when the resource has no natural client-chosen name, or for actions that are not "set this resource" (such as "send an email" or "charge a card"), with an idempotency key for safety.

**Checklist: your answer should mention**
- [ ] **client-chosen id** for PUT, **server-chosen id** for POST
- [ ] a retry of POST can create a **duplicate**
- [ ] a retry of PUT leaves the **same state**
- [ ] the definition of idempotent: same effect once or many times
- [ ] an **idempotency key**: generated once, sent on every retry, server returns the saved result
- [ ] a reason to use POST anyway (server-chosen ids, actions)
