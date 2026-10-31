## Approach

`json.dump(data, f, ...)` writes to a file object; `json.load(f)` reads from one. Pass `indent=2`, `sort_keys=True` and `ensure_ascii=False`, and open the file with `encoding="utf-8"` so the `é` is written as real UTF-8. `dump` adds no final newline, so write one yourself.

## Code

```python
import json


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
```

## Complexity

O(n) for the size of the data.

## Another way

Build the text with `json.dumps(...)` and write it in one call with `f.write(text + "\n")`. This is also a good start for a safe write (see the later problem on temporary files).
