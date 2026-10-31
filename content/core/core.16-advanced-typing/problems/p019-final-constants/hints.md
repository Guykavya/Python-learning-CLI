## Hint 1

Which module do you import `Final` from? Where does the annotation go: before or after the `=`? And what does a type checker do when it sees a second assignment to a name that is `Final`?

## Hint 2

The shape is `NAME: Final[type] = value`. With no brackets (`NAME: Final = value`) the checker infers the type from the value. Inside a class body the rule is the same.

## Hint 3

```
from typing import Final

MAX_RETRIES: Final = 3
API_URL: Final[str] = "..."
...
class Config:
    DEFAULT_PORT: Final[int] = 8080

def retry_delay(attempt: int) -> float:
    if attempt < 0: raise ValueError
    return min(BASE_DELAY * 2 ** attempt, MAX_DELAY)
```
