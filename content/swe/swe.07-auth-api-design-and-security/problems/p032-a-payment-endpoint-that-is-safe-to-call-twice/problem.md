# A payment endpoint that is safe to call twice

Chapter sections 13.1 to 13.6. A client sends `POST /payments` and the reply is lost. It cannot know whether the money moved, so it retries, and a naive server charges **twice**. The protocol of the chapter fixes it: the client sends an `Idempotency-Key` header and repeats the **same key** on every retry of the same payment.

You write the whole server side in `solution.py`, in two layers: a plain class that holds the logic, and a thin HTTP endpoint on top of it. The money moves through a **provider** object given from outside (in the tests a fake that counts charges). Never charge a real card in a test.

The starter already has `ProviderError` and `USERS = {"t-asha": "asha", "t-ravi": "ravi"}` (the token on the left, the user name on the right).

## 1. `PaymentService(provider)` and `service.create(user, key, body)`

`provider.charge(user, amount_cents)` returns a charge id (text such as `"ch_1"`), or raises `ProviderError` when the provider is down. `body` is a dict `{"amount_cents": 2500}`. `create` returns a tuple **`(status, response_body, replayed)`**:

| Situation | Result |
|---|---|
| key never seen for this user | claim the key, call the provider **once**, answer `201` with `{"charge_id": "...", "amount_cents": 2500}`, `replayed=False` |
| same user, same key, same body, first call **finished** | the **stored** status and body, `replayed=True`, **no** new charge |
| same user, same key, **different** body | `422` `{"detail": ...}`, no charge |
| same user, same key, same body, first call **still running** | `409` `{"detail": ...}`, no charge |
| the provider raises `ProviderError` | release the key, answer `502` `{"detail": ...}`; a retry with the same key may charge (a failure is not stored) |
| the provider raises any other exception | release the key and let the exception go up |

Keys are **per user**: Ravi using the key that Asha used is a different payment (chapter, "Try it: key scope"). Two bodies are "the same" when their `dict`s are equal (a hash of the sorted JSON is a good fingerprint).

**The race.** Two requests with the same key can arrive at the same moment. A "check, then insert" in two steps lets both through (see the next problem). Claim the key and mark it *in progress* in one step under a `threading.Lock`. And do **not** hold that lock while you call the provider: the provider is slow, and the second request must be able to answer `409` meanwhile. Take the lock again to store the result.

## 2. `build_app(provider)`

Returns a FastAPI app with `app.state.service` set to the `PaymentService`, and one route **`POST /payments`**:

- header `Authorization: Bearer <token>`; unknown or missing token: `401`;
- header `Idempotency-Key` required: `400` when it is missing;
- JSON body `{"amount_cents": n}` with `n` an integer, `0 < n <= 1_000_000`, no extra fields; otherwise `422` (a pydantic model does this for you);
- the status and body come from `service.create`; a replay has the response header `Idempotent-Replayed: true`; a `409` has `Retry-After: 1`.

## Example

```text
POST /payments  Idempotency-Key: k1  {"amount_cents": 2500}  -> 201 {"charge_id": "ch_1", "amount_cents": 2500}
POST /payments  Idempotency-Key: k1  {"amount_cents": 2500}  -> 201 same body, header Idempotent-Replayed: true
POST /payments  Idempotency-Key: k1  {"amount_cents": 9900}  -> 422   (same key, other body)
POST /payments  Idempotency-Key: k2  {"amount_cents": 2500}  -> 201 {"charge_id": "ch_2", ...}   (new key, new payment)
provider.charges after these four calls: 2
```

The tests call the endpoint 2, 3 and 10 times with one key and count the provider's charges. They also start a first call that is blocked inside the provider, and check that a second call with the same key gets `409` at once instead of waiting or charging again.
