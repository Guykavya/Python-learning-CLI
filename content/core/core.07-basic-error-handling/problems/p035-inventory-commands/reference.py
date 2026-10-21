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
