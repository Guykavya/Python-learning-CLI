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





class FakeClock:
    """Time that moves only when a test says so. Call it to read the time: clock() -> seconds."""

    def __init__(self, start=0.0):
        self.t = float(start)

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds
        return self.t



@pytest.fixture
def clock():
    return FakeClock(1000.0)


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "queue.db")
