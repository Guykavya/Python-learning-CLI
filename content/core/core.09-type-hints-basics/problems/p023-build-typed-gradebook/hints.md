## Hint 1

Start with the types, before any code. `parse_line` may fail, so its result is a pair **or** `None`. `load` returns a dict from name to a list of scores. Which functions can return `None`, and which return a plain value?

## Hint 2

For `parse_line`, split on `","` and look at the length of the list. Convert the score inside a `try/except ValueError`. For `load`, call `parse_line` and skip results that `is None`. For sorting: a key that sorts by `-average` and then `name` gives "highest first, ties by name".

## Hint 3

```
def parse_line(line) -> tuple[str, int] | None:
    parts = line.split(",")
    if len(parts) != 2: return None
    name = parts[0].strip()
    try: score = int(parts[1])
    except ValueError: return None
    if name == "" or score < 0 or score > 100: return None
    return name, score

ranking: sorted(((n, average(s)) for n, s in book.items()), key=lambda p: (-p[1], p[0]))
best_student: first item of ranking, or None
```
