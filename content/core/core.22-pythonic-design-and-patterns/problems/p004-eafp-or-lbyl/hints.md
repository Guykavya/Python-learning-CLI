## Hint 1

For each function ask: what does the check cost, and what could go wrong between the check
and the use? Which built-in method does "look up, or use this default" in one step? Which one
does "look up, or create and store this" in one step?

## Hint 2

Pick the tool per function.

```
get_port       -> int(config.get("port", 8080))
add_word       -> index.setdefault(word, []).append(line_no)
read_or_default-> try: open and read   except FileNotFoundError: return default
display_name   -> name = getattr(obj, "name", None); None means "ANON"
parse_int      -> try: return int(text)   except ValueError: return None
```
Careful: `except` must name the one error you expect. What happens to a `PermissionError`
if you write `except OSError`?
