import pytest

from solution import parse_args


def test_example():
    ns = parse_args(["a.txt", "b.txt", "-v", "--limit", "3"])
    assert ns.paths == ["a.txt", "b.txt"], "Positional paths: nargs='+' gives a list."
    assert ns.verbose is True, "-v sets verbose to True."
    assert ns.limit == 3, "--limit must be an int: use type=int."
    assert ns.mode == "copy", "The default mode is copy."


def test_defaults():
    ns = parse_args(["x"])
    assert (ns.paths, ns.verbose, ns.limit, ns.mode) == (["x"], False, 10, "copy"), "Defaults: verbose False, limit 10, mode copy."


def test_long_flag_and_mode():
    ns = parse_args(["--verbose", "--mode", "move", "p"])
    assert ns.verbose is True and ns.mode == "move" and ns.paths == ["p"], "--verbose is the long form of -v; options can come before the paths."


def test_no_paths_exits():
    with pytest.raises(SystemExit) as info:
        parse_args(["-v"])
    assert info.value.code == 2, "At least one path is required. Use nargs='+', not '*'."


def test_bad_limit_exits():
    with pytest.raises(SystemExit) as info:
        parse_args(["a", "--limit", "abc"])
    assert info.value.code == 2, "type=int makes argparse reject 'abc' by itself."


def test_bad_mode_exits():
    with pytest.raises(SystemExit) as info:
        parse_args(["a", "--mode", "zip"])
    assert info.value.code == 2, "Use choices=['copy', 'move']."


def test_uses_the_given_list():
    assert parse_args(["only"]).paths == ["only"], "Call parser.parse_args(argv) with the list you were given, not sys.argv."
