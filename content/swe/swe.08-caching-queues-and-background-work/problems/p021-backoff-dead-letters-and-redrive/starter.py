import json
import random
import sqlite3
from contextlib import closing


def backoff_delay(attempt, base=2.0, cap=300.0, rng=random.random):
    return base                                   # TODO: exponential, capped, equal jitter


def process_one(queue, handler, worker, *, permanent=(), base=2.0, cap=300.0, rng=random.random):
    # TODO: reserve, run, complete or fail
    return None


def dead_letters(queue):
    return []


def redrive(queue, job_id):
    return False


def redrive_all(queue, limit=None):
    return 0
