# Explain: what does Optional really mean?

Meera reads some old code with these three headers and is confused:

```python
from typing import Optional

def send_a(message: str, to: Optional[str]) -> str: ...
def send_b(message: str, to: str = "everyone") -> str: ...
def send_c(message: str, to: str | None = None) -> str: ...
```

She says: "`Optional` means I can leave the argument out, so `send_a("hi")` must work."

In `answer.md` (about 120 to 250 words), explain:

1. What does `Optional[str]` mean? How would you write the same hint with `|`, which is what this
   course uses?
2. Is Meera right? Say which of `send_a("hi")`, `send_b("hi")` and `send_c("hi")` can be called
   without the second argument, and what actually decides that.
3. Inside `send_c`, the body wants to write `to.upper()`. What error does mypy report if the code
   does this directly, and which check makes it safe?
4. Why is `to: str = None` a bad hint?
