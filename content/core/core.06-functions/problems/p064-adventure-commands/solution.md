## Approach

The design has three layers.

1. **Data**: the world is a dict of rooms; the game state is a separate dict. Items that can move
   live in the state, as copies, so the world is never changed and every game starts fresh.
2. **Handlers**: one small function per verb, all with the same signature
   `(state, world, arg)`, each returning text. They are easy to test on their own.
3. **Dispatch**: `COMMANDS` maps verbs to handlers. `handle` expands aliases, parses, looks the
   verb up, and calls whatever it finds. Adding a verb means writing one function and adding one
   entry; `help` reads the same table, so it is always complete.

`play` is the only place with a loop over input, which in the full project would be `input()` and
`print()`.

## Code

```python
WORLD = {
    "hall": {"description": "A dusty hall.", "exits": {"north": "library", "east": "kitchen"}, "items": ["lamp"]},
    "library": {"description": "Shelves of old books.", "exits": {"south": "hall"}, "items": ["book", "key"]},
    "kitchen": {"description": "It smells of bread.", "exits": {"west": "hall"}, "items": []},
}


def new_game(world):
    """Return {'room': 'hall', 'inventory': [], 'items': {room: copy of its items}}."""
    return {
        "room": "hall",
        "inventory": [],
        "items": {name: room["items"][:] for name, room in world.items()},
    }


def parse(line):
    """Return (verb, argument) from a command line, lowercased."""
    words = line.lower().split()
    if not words:
        return "", ""
    return words[0], " ".join(words[1:])


def do_look(state, world, arg):
    room = world[state["room"]]
    items = state["items"][state["room"]]
    seen = ", ".join(items) if items else "nothing"
    exits = ", ".join(sorted(room["exits"]))
    return f"{room['description']}\nExits: {exits}\nYou see: {seen}"


def do_go(state, world, arg):
    if not arg:
        return "Go where?"
    exits = world[state["room"]]["exits"]
    if arg not in exits:
        return f"You can't go {arg}."
    state["room"] = exits[arg]
    return do_look(state, world, "")


def do_take(state, world, arg):
    if not arg:
        return "Take what?"
    here = state["items"][state["room"]]
    if arg not in here:
        return f"There is no {arg} here."
    here.remove(arg)
    state["inventory"].append(arg)
    return f"Taken: {arg}"


def do_drop(state, world, arg):
    if not arg:
        return "Drop what?"
    if arg not in state["inventory"]:
        return f"You don't have {arg}."
    state["inventory"].remove(arg)
    state["items"][state["room"]].append(arg)
    return f"Dropped: {arg}"


def do_inventory(state, world, arg):
    if not state["inventory"]:
        return "You are carrying nothing."
    return "You are carrying: " + ", ".join(state["inventory"])


def do_help(state, world, arg):
    return "Commands: " + ", ".join(sorted(COMMANDS))


def do_quit(state, world, arg):
    return "Goodbye."


COMMANDS = {
    "look": do_look,
    "go": do_go,
    "take": do_take,
    "drop": do_drop,
    "inventory": do_inventory,
    "help": do_help,
    "quit": do_quit,
}

ALIASES = {"n": "go north", "s": "go south", "e": "go east", "w": "go west", "l": "look", "i": "inventory"}


def expand(line):
    """Replace a whole-line alias by its full command."""
    return ALIASES.get(line.strip().lower(), line)


def handle(state, world, line):
    """Return the text produced by one command line."""
    verb, arg = parse(expand(line))
    if not verb:
        return "Say something."
    handler = COMMANDS.get(verb)
    if handler is None:
        return f"I don't understand '{verb}'."
    return handler(state, world, arg)


def play(lines, world=WORLD):
    """Play a new game with these lines; return the outputs, stopping after 'quit'."""
    state = new_game(world)
    outputs = []
    for line in lines:
        outputs.append(handle(state, world, line))
        if parse(expand(line))[0] == "quit":
            break
    return outputs
```

## Complexity

Each command is O(size of the room's item list or inventory); dispatch is one dict lookup.

## Another way

Handlers could return a **new** state instead of mutating it (`return new_state, text`). That is
purer and makes "undo" easy (keep old states), at the cost of copying. Whichever you choose for the
project, choose it once and use it for every handler.
