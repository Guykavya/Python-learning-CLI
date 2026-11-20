import hashlib
import json
import threading

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

USERS = {"t-asha": "asha", "t-ravi": "ravi"}


class ProviderError(Exception):
    """The payment provider is down."""


class PaymentService:
    def __init__(self, provider):
        self.provider = provider
        self.lock = threading.Lock()
        self.records = {}

    def create(self, user, key, body):
        """Return (status, response_body, replayed)."""
        # TODO: claim (user, key) under the lock, charge WITHOUT the lock, store the result under the lock
        raise NotImplementedError("write PaymentService.create")


def build_app(provider):
    app = FastAPI()
    app.state.service = PaymentService(provider)
    # TODO: POST /payments
    return app
