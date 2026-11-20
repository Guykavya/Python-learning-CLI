"""Course helpers for this problem, copied from the chapter (swe.08). The tests receive them as fixtures.
Your solution never imports this file: everything it needs arrives as a function argument."""
import fnmatch
import json
import math
import random
import signal
import sqlite3
import threading
import time
from contextlib import closing

import pytest



class ProviderTimeout(Exception):
    pass


class FakeMailProvider:
    """Stands in for an e-mail API. `outbox` is what recipients really received."""

    def __init__(self, honours_idempotency_keys=True):
        self.honours_keys = honours_idempotency_keys
        self.outbox, self._by_key = [], {}
        self.lose_next_response = False

    def send(self, to, subject, body, idempotency_key=None):
        if self.honours_keys and idempotency_key is not None and idempotency_key in self._by_key:
            return self._by_key[idempotency_key]                    # a repeat: do not send again
        message_id = f"msg-{len(self.outbox) + 1}"
        self.outbox.append({"id": message_id, "to": to, "subject": subject})
        if idempotency_key is not None:
            self._by_key[idempotency_key] = message_id
        if self.lose_next_response:
            self.lose_next_response = False
            raise ProviderTimeout("sent, but the response never arrived")
        return message_id


class Crash(BaseException):
    """Simulates the PROCESS DYING. It derives from BaseException so the worker's `except Exception` cannot catch it."""


class CrashAt:
    def __init__(self, point=None):
        self.point = point

    def hit(self, name):
        if name == self.point:
            self.point = None                                     # crash once
            raise Crash(name)


@pytest.fixture
def crash_at():
    return CrashAt


@pytest.fixture
def crash_type():
    return Crash
