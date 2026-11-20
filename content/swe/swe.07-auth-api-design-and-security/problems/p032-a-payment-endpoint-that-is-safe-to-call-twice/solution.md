## Approach

```python
import hashlib
import json
import threading

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

USERS = {"t-asha": "asha", "t-ravi": "ravi"}


class ProviderError(Exception):
    pass


def fingerprint(body):
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class PaymentService:
    def __init__(self, provider):
        self.provider = provider
        self.lock = threading.Lock()
        self.records = {}                       # (user, key) -> {"fp", "status", "response"}

    def create(self, user, key, body):
        fp = fingerprint(body)
        slot = (user, key)                      # keys are scoped to the user
        with self.lock:                         # check AND claim in one step
            record = self.records.get(slot)
            if record is None:
                self.records[slot] = {"fp": fp, "status": "in_progress", "response": None}
            elif record["fp"] != fp:
                return 422, {"detail": "this Idempotency-Key was already used with a different request"}, False
            elif record["status"] == "completed":
                code, stored = record["response"]
                return code, dict(stored), True
            else:
                return 409, {"detail": "a request with this key is still being processed"}, False
        try:                                    # the slow part runs WITHOUT the lock
            charge_id = self.provider.charge(user, body["amount_cents"])
        except ProviderError:
            with self.lock:
                del self.records[slot]          # a failure is not stored: the retry may run properly
            return 502, {"detail": "the payment provider failed; retry with the same key"}, False
        except BaseException:
            with self.lock:
                del self.records[slot]
            raise
        response = {"charge_id": charge_id, "amount_cents": body["amount_cents"]}
        with self.lock:
            self.records[slot].update(status="completed", response=(201, response))
        return 201, dict(response), False


class PaymentIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount_cents: int = Field(gt=0, le=1_000_000)


def build_app(provider):
    app = FastAPI()
    service = PaymentService(provider)
    app.state.service = service

    @app.post("/payments")
    def post_payment(body: PaymentIn, authorization: str = Header(default=""),
                     idempotency_key: str | None = Header(default=None)):
        user = USERS.get(authorization.removeprefix("Bearer "))
        if user is None:
            raise HTTPException(401, "login required")
        if not idempotency_key:
            raise HTTPException(400, "the Idempotency-Key header is required")
        code, response, replayed = service.create(user, idempotency_key, body.model_dump())
        headers = {}
        if replayed:
            headers["Idempotent-Replayed"] = "true"
        if code == 409:
            headers["Retry-After"] = "1"
        return JSONResponse(response, status_code=code, headers=headers)

    return app
```

Walk through the three phases of `create`. **Claim** (under the lock): the first request for a `(user, key)` writes the record `in_progress`; every other request reads it and gets 422, the stored replay, or 409. Because lookup and insert happen under one lock, exactly one caller can be the claimer, which is what a `PRIMARY KEY (user_id, key)` does in the chapter's SQLite version. **Work** (no lock): the provider call. If it held the lock, a duplicate would wait instead of answering 409, and a slow provider would freeze all other payments. **Finish** (under the lock): store the response so that retries get exactly the same status and body.

A repeat call returns `dict(stored)`, a copy, so a caller who changes the dictionary cannot damage the stored answer.

The chapter's version puts the debit and the "completed" mark in one SQL transaction. Here the provider is outside our database, so the equivalent is the rule of section 13.3: pass **your key on to the provider** as its idempotency key, so that the one case the code cannot cover (the process dies after the provider charged but before we stored the result) is still safe.

## Complexity

O(1) per call and O(number of payments) memory. In production the records are a table with the unique key and a clean-up job for old rows (and a timeout that lets a retry take over a claim that has been "in progress" for minutes, section 13.4).

## Another way

Keep the records in a database table with `PRIMARY KEY (user_id, key)` and claim the key with an `INSERT` that raises `IntegrityError` when the key exists (section 13.4). Then the database does the locking, it also works across several workers, and the claim survives a restart. The in-memory lock only protects one process.
