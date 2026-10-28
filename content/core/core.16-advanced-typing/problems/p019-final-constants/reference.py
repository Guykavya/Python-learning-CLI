from typing import Final

MAX_RETRIES: Final = 3
API_URL: Final[str] = "https://api.example.com"
BASE_DELAY: Final[float] = 0.5
MAX_DELAY: Final[float] = 8.0
ALLOWED_METHODS: Final = ("GET", "POST")


class Config:
    DEFAULT_PORT: Final[int] = 8080


def retry_delay(attempt: int) -> float:
    if attempt < 0:
        raise ValueError("attempt must not be negative")
    return min(BASE_DELAY * 2 ** attempt, MAX_DELAY)
