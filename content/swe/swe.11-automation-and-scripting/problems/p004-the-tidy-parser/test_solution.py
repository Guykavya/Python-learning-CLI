import subprocess
import sys
from pathlib import Path

import pytest

import solution
from solution import build_parser


def parse(*argv):
    return build_parser().parse_args(list(argv))


def exit_code(*argv):
    with pytest.raises(SystemExit) as e:
        parse(*argv)
    return e.value.code


def test_organize_with_counted_verbose():
    ns = parse("-vv", "organize", "Downloads")
    assert ns.command == "organize", "Subcommands need dest='command' so main() knows which one was chosen."
    assert ns.verbose == 2, "-vv must count to 2: action='count'."
    assert ns.folder == Path("Downloads") and isinstance(ns.folder, Path), "Use type=Path for the folder."
    assert ns.dry_run is False


def test_dry_run_short_and_long():
    assert parse("organize", "x", "-n").dry_run is True, "-n is the short form of --dry-run (store_true)."
    assert parse("organize", "--dry-run", "x").dry_run is True


def test_verbose_defaults_to_zero():
    assert parse("undo", "x").verbose == 0, "Without -v the count must be 0, not None: set default=0."


def test_undo_has_only_a_folder():
    ns = parse("undo", "photos")
    assert ns.command == "undo" and ns.folder == Path("photos")
    assert exit_code("undo", "photos", "--dry-run") == 2, "undo has no --dry-run option in this tool."


def test_dupes_min_size_is_an_int_with_default_1():
    assert parse("dupes", "x").min_size == 1, "--min-size defaults to 1 (empty files are ignored)."
    ns = parse("dupes", "x", "--min-size", "10")
    assert ns.min_size == 10 and isinstance(ns.min_size, int), "type=int: argparse converts '10' to 10."


def test_usage_errors_exit_2(capsys):
    assert exit_code() == 2, "No subcommand: required=True makes it a usage error (exit 2)."
    assert exit_code("organise", "x") == 2, "A misspelt subcommand is a usage error."
    assert exit_code("organize") == 2, "The folder is required."
    assert exit_code("dupes", "x", "--min-size", "abc") == 2, "argparse refuses 'abc' for an int option."
    assert exit_code("organize", "x", "-v") == 2, "-v is global: it must come BEFORE the subcommand, so here it is unknown."


def test_help_and_version_exit_0(capsys):
    assert exit_code("--help") == 0, "--help prints and exits 0."
    out = capsys.readouterr().out
    for word in ("organize", "undo", "dupes"):
        assert word in out, f"The help must list the subcommand {word!r}."
    assert exit_code("--version") == 0
    assert "tidy 1.0" in capsys.readouterr().out, "--version prints 'tidy 1.0'."


def test_help_as_a_real_program():
    r = subprocess.run([sys.executable, solution.__file__, "--help"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and "usage: tidy" in r.stdout, f"python solution.py --help must exit 0 and show 'usage: tidy'. stderr: {r.stderr}"
