# Read a file or fall back to a default

Write `read_or_default(path, default="")` in `solution.py`.

- Return the full text of the UTF-8 file at `path`.
- If the file **does not exist**, return `default`.
- Catch only that one error. Any other problem (for example when `path` is a folder) must still raise.
- An existing empty file returns `""`, not `default`.

**Example**

```python
read_or_default("settings.txt", "none")   # text, or "none" if settings.txt is missing
```
