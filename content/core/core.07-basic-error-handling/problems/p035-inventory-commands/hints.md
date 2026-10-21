## Hint 1

Split the work: small handler functions that only know their own verb and **raise** when
something is wrong, and one loop in `process` that turns those exceptions into replies. Why is
that better than building error strings inside every handler?

## Hint 2

A missing item: `stock[item]` already raises `KeyError(item)`. You do not have to check first:
let it escape from the handler and translate it once in `process` with `e.args[0]`.

## Hint 3

```
HANDLERS = {"add": do_add, "remove": do_remove, "show": do_show, "list": do_list}

for command in commands:
    try:
        words = command.split(); empty? raise ValueError("empty command")
        verb = words[0].lower(); unknown? raise ValueError(...)
        replies.append(HANDLERS[verb](stock, words[1:]))
    except ValueError as e: replies.append(f"error: {e}")
    except KeyError as e: replies.append(f"error: no item {e.args[0]!r} in stock")
```
Careful: `HANDLERS[verb]` would also raise `KeyError` for an unknown verb, and you would report
it as a missing **item**. Check the verb with `in` first.
