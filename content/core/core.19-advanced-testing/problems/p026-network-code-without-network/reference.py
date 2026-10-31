import json
import urllib.error
import urllib.request


def default_get(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.code, ""


def fetch_title(url, http_get=None):
    if http_get is None:
        http_get = default_get
    status, body = http_get(url)
    if status == 404:
        return None
    if status != 200:
        raise RuntimeError(f"HTTP {status} for {url}")
    try:
        data = json.loads(body)
    except ValueError:
        raise ValueError(f"bad JSON from {url}") from None
    return data["title"]
