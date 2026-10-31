import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen


class KVHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def start_server(store):
    """Return (server, thread, base_url) with serve_forever running in a daemon thread."""
    raise NotImplementedError("start_server")


def stop_server(server, thread):
    pass


def get_json(url, timeout=5):
    return 0, None


def post_json(url, payload, timeout=5):
    return 0, None
