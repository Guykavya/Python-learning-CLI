MAX_RETRIES = 3
API_URL = "https://api.example.com"
BASE_DELAY = 0.5
MAX_DELAY = 8.0
ALLOWED_METHODS = ("GET", "POST")


class Config:
    DEFAULT_PORT = 8080


def retry_delay(attempt):
    # TODO: add the hints; raise ValueError for a negative attempt
    return min(BASE_DELAY * 2 ** attempt, MAX_DELAY)
