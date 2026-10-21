# A text-adventure command engine

This is the assessed stepping stone for the module project. Build a small text-adventure engine
**driven by a dict of functions**. `starter.py` gives you the world:

```python
WORLD = {
    "hall":    {"description": "A dusty hall.",        "exits": {"north": "library", "east": "kitchen"}, "items": ["lamp"]},
    "library": {"description": "Shelves of old books.", "exits": {"south": "hall"},                       "items": ["book", "key"]},
    "kitchen": {"description": "It smells of bread.",   "exits": {"west": "hall"},                        "items": []},
}
```

Write these functions.

**`new_game(world)`** returns a new state dict:
`{"room": "hall", "inventory": [], "items": {room name: a COPY of that room's item list}}`.
Taking and dropping change `state["items"]`, never `world`.

**`parse(line)`** returns `(verb, argument)`: lowercase, words split on whitespace; the verb is
the first word, the argument the remaining words joined by single spaces.
`parse("  Take  OLD book ")` is `("take", "old book")`; `parse("look")` is `("look", "")`;
`parse("")` is `("", "")`.

**Handlers**, every one with the signature `handler(state, world, arg)` and returning the text to
show:

| verb | behaviour and exact text |
|---|---|
| `look` | three lines joined by `"\n"`: the description; `Exits: ` + exit directions sorted, joined by `", "`; `You see: ` + items in the room joined by `", "`, or `You see: nothing` |
| `go` | no argument: `Go where?`. Unknown direction: `You can't go DIR.` Otherwise move and return the `look` text of the new room |
| `take` | no argument: `Take what?`. Not in the room: `There is no ITEM here.` Otherwise move it from the room to the end of the inventory: `Taken: ITEM` |
| `drop` | no argument: `Drop what?`. Not carried: `You don't have ITEM.` Otherwise move it to the end of the room's items: `Dropped: ITEM` |
| `inventory` | `You are carrying: a, b` in the order taken, or `You are carrying nothing.` |
| `help` | `Commands: ` + all verbs in `COMMANDS`, sorted, joined by `", "` |
| `quit` | `Goodbye.` |

**`COMMANDS`**: a module-level dict from each verb above to its handler function.
**`ALIASES`**: a module-level dict from short words to full lines:
`{"n": "go north", "s": "go south", "e": "go east", "w": "go west", "l": "look", "i": "inventory"}`.

**`handle(state, world, line)`**: if the whole lowercased, stripped line is an alias, replace it
by the full line. Then parse it. An empty verb returns `Say something.`; an unknown verb returns
`I don't understand 'VERB'.`; otherwise call the handler from `COMMANDS` (look it up there, so a
verb added to `COMMANDS` later works without editing `handle`).

**`play(lines, world=WORLD)`**: start a new game, handle each line in turn, collect the outputs
in a list, and stop after a `quit` command. Return the list.

**Example**

```python
play(["look", "take lamp", "n", "take KEY", "take sword", "i", "s", "drop lamp", "l", "dance", "quit", "look"])
```
returns
```python
['A dusty hall.\nExits: east, north\nYou see: lamp',
 'Taken: lamp',
 'Shelves of old books.\nExits: south\nYou see: book, key',
 'Taken: key',
 'There is no sword here.',
 'You are carrying: lamp, key',
 'A dusty hall.\nExits: east, north\nYou see: nothing',
 'Dropped: lamp',
 'A dusty hall.\nExits: east, north\nYou see: lamp',
 "I don't understand 'dance'.",
 'Goodbye.']
```
