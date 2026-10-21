WORLD = {
    "hall": {"description": "A dusty hall.", "exits": {"north": "library", "east": "kitchen"}, "items": ["lamp"]},
    "library": {"description": "Shelves of old books.", "exits": {"south": "hall"}, "items": ["book", "key"]},
    "kitchen": {"description": "It smells of bread.", "exits": {"west": "hall"}, "items": []},
}


def new_game(world):
    """Return {'room': 'hall', 'inventory': [], 'items': {room: copy of its items}}."""
    pass


def parse(line):
    """Return (verb, argument) from a command line, lowercased."""
    pass


# Write the handlers do_look, do_go, do_take, do_drop, do_inventory, do_help, do_quit here.
# Every handler: handler(state, world, arg) -> str


COMMANDS = {}
ALIASES = {}


def handle(state, world, line):
    """Return the text produced by one command line."""
    pass


def play(lines, world=WORLD):
    """Play a new game with these lines; return the outputs, stopping after 'quit'."""
    pass
