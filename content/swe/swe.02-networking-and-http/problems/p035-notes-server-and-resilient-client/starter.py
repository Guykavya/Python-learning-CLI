import json
import random
import socket
import threading
import time

import httpx


class RequestFailed(Exception):
    def __init__(self, message, status=None, attempts=1):
        super().__init__(message)
        self.status = status
        self.attempts = attempts


class NotesServer:
    def __init__(self):
        self.connections = 0
        self.requests = 0
        # TODO: listening socket on ("127.0.0.1", 0); port and base

    def __enter__(self):
        # TODO: start the accept loop in a daemon thread
        return self

    def __exit__(self, *exc):
        # TODO: stop the loop, close the listener
        pass


class NotesClient:
    def __init__(self, client, sleep=time.sleep, rng=random, attempts=4):
        self.client = client
        self.sleep = sleep
        self.rng = rng
        self.attempts = attempts

    def list_notes(self):
        raise NotImplementedError

    def get_note(self, note_id):
        raise NotImplementedError

    def create(self, text, idempotency_key=None):
        raise NotImplementedError
