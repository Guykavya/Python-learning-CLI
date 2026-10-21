import copy
import solution
from solution import WORLD, new_game, parse, handle, play, COMMANDS, ALIASES

HALL = "A dusty hall.\nExits: east, north\nYou see: lamp"
LIBRARY = "Shelves of old books.\nExits: south\nYou see: book, key"


def test_parse():
    assert parse("  Take  OLD book ") == ("take", "old book"), "Lowercase, split, verb first, rest joined by single spaces."
    assert parse("look") == ("look", "")
    assert parse("") == ("", "")
    assert parse("   ") == ("", "")


def test_new_game_copies_items():
    state = new_game(WORLD)
    assert state["room"] == "hall" and state["inventory"] == []
    assert state["items"] == {"hall": ["lamp"], "library": ["book", "key"], "kitchen": []}
    assert state["items"]["hall"] is not WORLD["hall"]["items"], (
        "state['items'] must hold COPIES of the room item lists, or taking items changes WORLD.")


def test_example_game():
    lines = ["look", "take lamp", "n", "take KEY", "take sword", "i", "s", "drop lamp", "l", "dance", "quit", "look"]
    assert play(lines) == [
        HALL, "Taken: lamp", LIBRARY, "Taken: key", "There is no sword here.", "You are carrying: lamp, key",
        "A dusty hall.\nExits: east, north\nYou see: nothing", "Dropped: lamp", HALL,
        "I don't understand 'dance'.", "Goodbye."], (
        "Compare your outputs with the example in problem.md line by line. play must stop after quit.")


def test_movement_errors():
    assert play(["go", "go west", "go north", "go north"]) == [
        "Go where?", "You can't go west.", LIBRARY, "You can't go north."]


def test_take_drop_errors():
    assert play(["take", "drop", "drop lamp", "take lamp", "take lamp", "inventory"]) == [
        "Take what?", "Drop what?", "You don't have lamp.", "Taken: lamp", "There is no lamp here.",
        "You are carrying: lamp"]


def test_empty_room_and_inventory():
    assert play(["e", "i", ""]) == [
        "It smells of bread.\nExits: west\nYou see: nothing", "You are carrying nothing.", "Say something."]


def test_help():
    assert play(["help"]) == ["Commands: drop, go, help, inventory, look, quit, take"], (
        "help lists sorted(COMMANDS), so it can never get out of date.")


def test_aliases():
    assert ALIASES == {"n": "go north", "s": "go south", "e": "go east", "w": "go west", "l": "look", "i": "inventory"}
    assert play(["N", " s ", "L"]) == [LIBRARY, HALL, HALL]


def test_world_never_changes():
    before = copy.deepcopy(WORLD)
    play(["take lamp", "n", "take book", "drop lamp", "s", "e", "drop book"])
    assert WORLD == before, "Playing changed WORLD. Copy each room's item list in new_game."


def test_games_are_independent():
    play(["take lamp", "quit"])
    assert play(["look"]) == [HALL], (
        "A new play() call must start a fresh game. Is state stored in a global or a mutable default?")


def test_commands_table():
    assert set(COMMANDS) == {"look", "go", "take", "drop", "inventory", "help", "quit"}
    assert all(callable(f) for f in COMMANDS.values()), "COMMANDS values must be the handler functions themselves."


def test_handle_uses_the_table():
    COMMANDS["xyzzy"] = lambda state, world, arg: "Nothing happens."
    try:
        state = new_game(WORLD)
        result = handle(state, WORLD, "XYZZY")
    finally:
        del COMMANDS["xyzzy"]
    assert result == "Nothing happens.", (
        "handle must look the verb up in COMMANDS (a dispatch table), not use an if/elif chain.")


def test_handlers_share_one_signature():
    state = new_game(WORLD)
    for verb, func in COMMANDS.items():
        if verb != "quit":
            assert isinstance(func(state, WORLD, ""), str), f"COMMANDS[{verb!r}](state, world, '') must return a string."


def test_custom_world():
    tiny = {"hall": {"description": "Tiny.", "exits": {}, "items": ["coin"]}}
    assert play(["look", "take coin", "look"], world=tiny) == [
        "Tiny.\nExits: \nYou see: coin", "Taken: coin", "Tiny.\nExits: \nYou see: nothing"]
