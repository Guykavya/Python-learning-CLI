## Approach

The model answer is in `answer.md`. The central contrast: `PUT` names the **result** ("this resource has this content"), `POST` names an **action** ("do this"). Results can be repeated, actions cannot, unless the server remembers the attempt (the idempotency key).

You can see it in a test: run `POST` twice against a server and count the books; run `PUT` twice and count again (chapter section 21.5 shows this with payments).

## Complexity

Not applicable.

## Another way

Use `PUT` with a client-generated UUID for creation in public APIs where retries are frequent (mobile apps on bad networks), and `POST` with an `Idempotency-Key` for actions with side effects.

## Why it matters

The lost reply is the most common cause of double charges and duplicate orders. Knowing which design survives it is a core API skill.
