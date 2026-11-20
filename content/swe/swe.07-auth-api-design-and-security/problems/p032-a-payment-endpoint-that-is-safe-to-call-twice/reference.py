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
