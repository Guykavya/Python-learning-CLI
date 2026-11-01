## Approach

The model answer is in `answer.md`. A good review sorts problems by *why they matter*:
readability (names, comments), design (flag argument, mixed levels), safety (bare `except`,
unclosed file), and testability (side effects, globals, I/O inside logic). Then it proposes
small steps and starts with a test.

## Check your answer

- Did you find at least six problems and give the reason, not just "bad style"?
- Did you name the **flag argument** and say why it is a smell (two jobs, unclear call sites)?
- Did you see the **side effects**: input mutated, global `LOG`, `print`?
- Did you notice the file is never closed and `except:` is bare?
- Did your split have a **pure** core and one place for I/O?
- Did your first test **pin the old behavior** rather than the new design?

## Another way

A refactored version, for comparison (not required in your answer):

```python
def load_rate(path):
    with open(path) as fh:
        return json.load(fh)["rate"]

def row_total(row, rate=1.0):
    return row["price"] * row["qty"] * rate

def price_rows(rows, rate=1.0):
    return [{**row, "total": row_total(row, rate)} for row in rows]
```

Note the behavior question: the old code turned a broken row into total 0 and printed
`error`. Replacing it with an exception is a **behavior change**. A reviewer says so and asks
the author which is wanted; that is exactly what the first test (pinning old behavior)
makes visible.
