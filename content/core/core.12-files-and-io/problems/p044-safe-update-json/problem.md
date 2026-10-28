# safe_update_json: change a file or change nothing

A small program keeps its data in `data.json` and updates it many times. If the program crashes in the middle of a
write, the file must not be damaged. Write `safe_update_json(path, fn)` in `solution.py`:

1. Load the JSON from `path`. If the file does **not exist**, start with an empty dict `{}`.
   If the file exists but is not valid JSON, let `json.JSONDecodeError` go up.
2. Call `fn(data)`. `fn` may change `data` in place and return `None`, **or** return a new value. If it returns
   something that is not `None`, that value is the new data.
3. Write the new data **safely**: dump it into a temporary file in the same folder, then `os.replace` it over `path`.
4. Return the new data.

**Failure rules**

- If `fn` raises, the file is untouched, no temp file is left, and the error goes up.
- If the new data cannot be written as JSON (for example it contains a set), the old file is untouched, and the
  half-written temp file is deleted. The `TypeError` goes up.
- If `os.replace` fails with `OSError`, the old file is untouched, and the temp file is deleted.

**Example**

```python
def add_visit(data):
    data["visits"] = data.get("visits", 0) + 1

safe_update_json("stats.json", add_visit)   # {"visits": 1}  (file created)
safe_update_json("stats.json", add_visit)   # {"visits": 2}
```
