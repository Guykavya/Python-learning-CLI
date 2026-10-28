# Explain: when to use Any and when object

A teammate, Dev, writes this module and asks you to review it:

```python
import json
from typing import Any


def log(value: Any) -> None:
    print(f"[log] {value}")


def read_config(path: str) -> Any:
    with open(path) as f:
        return json.load(f)


config = read_config("app.json")
port = config["server"]["port"] + 1
retries: int = config["retries"]
```

Dev says: "`Any` means anything is allowed, and `object` means the same thing, so I use `Any`
everywhere because it is shorter to explain." mypy reports no error for this file.

In `answer.md` (about 150 to 300 words), explain:

1. Are `Any` and `object` really the same? Say what the checker does with each one.
2. For `log`, which of the two would you choose, and why? Does `log` need to look inside `value`?
3. What is the risk in `read_config` returning `Any`? Name a concrete bug that mypy would
   **not** report in the last two lines. What would you return instead, and what would the caller
   have to do?
4. Give one situation where `Any` is a reasonable choice.

See the model answer shown when you check.
