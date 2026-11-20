## Approach

```python
def parse_status(text):
    result = {"staged": [], "modified": [], "deleted": [], "untracked": []}
    for line in text.splitlines():
        if not line.strip():
            continue
        x, y, path = line[0], line[1], line[3:]
        if " -> " in path:
            path = path.split(" -> ")[-1]
        if len(path) >= 2 and path[0] == '"' and path[-1] == '"':
            path = path[1:-1]
        if line.startswith("??"):
            result["untracked"].append(path)
            continue
        if x not in " ?":
            result["staged"].append(path)
        if y == "M":
            result["modified"].append(path)
        if "D" in (x, y):
            result["deleted"].append(path)
    return result
```

The two status letters are positional: `line[0]` is the index, `line[1]` the working tree, and `line[2]` is always a space. That is why `.strip()` on the whole line would break ` M b.py` (it would turn it into `M b.py`, shifting every position).

Example: `MM c.py`: `x = "M"` is not in `" ?"`, so staged; `y = "M"`, so also modified.

## Complexity

`O(number of lines)`.

## Another way

`git status --porcelain=v1 -z` separates entries with NUL bytes and never quotes names; that is what scripts should use. Here we parse the human-readable form because it is what you see in a terminal.

## Why it matters

Tools such as prompts, editors and CI scripts read `status --porcelain` instead of the pretty `git status` text, which changes between git versions. This stable format is the interface.
