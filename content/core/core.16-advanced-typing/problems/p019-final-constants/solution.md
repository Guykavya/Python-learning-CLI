## Approach

`Final` tells the type checker "this name is bound once and never rebound". You write it as the
annotation, and the value still goes after the `=`. `Final[str]` states the type; plain `Final`
lets the checker infer it from the value (use the explicit form when the inferred type would be
too narrow or unclear, such as `Final[float]` for `0.5`).

## Code

```python
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
```

## Complexity

O(1).

## Another way

Without `Final`, a naming convention (capitals) is all that protects a constant, and a checker
cannot enforce it. For a tuple that must never change shape, `Final[tuple[str, ...]]` plus a real
tuple is stronger than `Final[list[str]]`, because a `Final` list can still be mutated with
`.append`. `Final` stops rebinding, not mutation.
