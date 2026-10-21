## Approach

Exceptions let each part of the program do one job. Handlers validate their own words and raise
`ValueError` with a precise message; a missing item raises `KeyError` all by itself. `process` is
the **boundary** between the program and the person: it is the only place that knows replies must
be strings starting with `error: `, so it is the only place that catches, and it catches exactly
the two types handlers are designed to raise. A `TypeError` from corrupt stock data is a bug and
escapes. Checks inside `do_remove` come before the line that changes the stock, so a refused
removal changes nothing.

## Code

```python
def parse_qty(text):
    try:
        qty = int(text)
    except ValueError:
        raise ValueError(f"quantity must be a positive whole number, got {text!r}") from None
    if qty <= 0:
        raise ValueError(f"quantity must be a positive whole number, got {text!r}")
    return qty


def do_add(stock, words):
    if len(words) != 2:
        raise ValueError("usage: add <item> <qty>")
    item, qty = words[0].lower(), parse_qty(words[1])
    stock[item] = stock.get(item, 0) + qty
    return f"{item}: {stock[item]}"


def do_remove(stock, words):
    if len(words) != 2:
        raise ValueError("usage: remove <item> <qty>")
    item, qty = words[0].lower(), parse_qty(words[1])
    have = stock[item]                       # KeyError if the item is not in stock
    if qty > have:
        raise ValueError(f"only {have} {item} in stock, cannot remove {qty}")
    stock[item] = have - qty
    return f"{item}: {stock[item]}"


def do_show(stock, words):
    if len(words) != 1:
        raise ValueError("usage: show <item>")
    item = words[0].lower()
    return f"{item}: {stock[item]}"


def do_list(stock, words):
    if words:
        raise ValueError("usage: list")
    if not stock:
        return "empty"
    return ", ".join(f"{item}: {stock[item]}" for item in sorted(stock))


HANDLERS = {"add": do_add, "remove": do_remove, "show": do_show, "list": do_list}


def run_one(command, stock):
    words = command.split()
    if not words:
        raise ValueError("empty command")
    verb, rest = words[0].lower(), words[1:]
    if verb not in HANDLERS:
        raise ValueError(f"unknown command {verb!r}; use add, remove, show or list")
    return HANDLERS[verb](stock, rest)


def process(commands, stock):
    """Run each command on stock; return one reply per command ('error: ...' for bad ones)."""
    replies = []
    for command in commands:
        try:
            replies.append(run_one(command, stock))
        except ValueError as e:
            replies.append(f"error: {e}")
        except KeyError as e:
            replies.append(f"error: no item {e.args[0]!r} in stock")
    return replies
```

## Complexity

O(total length of the commands), plus O(s log s) for each `list` with s items.

## Another way

Handlers could return `(ok, text)` pairs instead of raising. Every handler would then need
`return False, "..."` on each failure, and every helper they call (like `parse_qty`) would need
the same convention, with checks after each call. Exceptions skip all that plumbing: the failure
travels straight to the one place that knows what to do with it. The weak spot of the raising
design is `KeyError`: a `KeyError` from an unexpected place (a bug) would also be reported as a
missing item. Keeping `KeyError` confined to the single `stock[item]` lookups, and checking the
verb with `in`, keeps that risk small; raising `ValueError(f"no item {item!r} in stock")` from the
handlers instead removes it entirely.
