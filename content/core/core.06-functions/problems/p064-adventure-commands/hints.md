## Hint 1

Write and test `parse` and `do_look` first. Every other handler can reuse `do_look` or the state layout.

## Hint 2

The world must never change. In `new_game`, copy each room's item list: `{name: room["items"][:] for name, room in world.items()}`.

## Hint 3

```
COMMANDS = {"look": do_look, "go": do_go, "take": do_take, "drop": do_drop,
            "inventory": do_inventory, "help": do_help, "quit": do_quit}

def handle(state, world, line):
    key = line.strip().lower()
    line = ALIASES.get(key, line)
    verb, arg = parse(line)
    if not verb: return "Say something."
    handler = COMMANDS.get(verb)
    if handler is None: return f"I don't understand '{verb}'."
    return handler(state, world, arg)
```
`COMMANDS` must be defined after the handler functions, because it refers to them.

## Hint 4

```
def play(lines, world=WORLD):
    state = new_game(world)
    outputs = []
    for line in lines:
        outputs.append(handle(state, world, line))
        if parse(ALIASES.get(line.strip().lower(), line))[0] == "quit": break
    return outputs
```
