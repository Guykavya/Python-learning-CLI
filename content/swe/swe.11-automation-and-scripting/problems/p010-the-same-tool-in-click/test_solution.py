import subprocess
import sys

import pytest
from click.testing import CliRunner

import solution
from solution import cli


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None) for p in sorted(root.rglob("*"))}


@pytest.fixture
def messy(tmp_path):
    for name, data in {"a.pdf": b"pdf", "b.PNG": b"png", "README": b"none", ".hidden": b"h"}.items():
        (tmp_path / name).write_bytes(data)
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_help_lists_both_commands(runner):
    r = runner.invoke(cli, ["--help"])
    assert r.exit_code == 0, r.output
    assert "organize" in r.output and "undo" in r.output, "Register the commands under the names 'organize' and 'undo'."


def test_version(runner):
    r = runner.invoke(cli, ["--version"])
    assert r.exit_code == 0 and "1.0" in r.output, "Add @click.version_option('1.0', prog_name='tidy') to the group."


def test_dry_run_changes_nothing(runner, messy):
    before = snapshot(messy)
    r = runner.invoke(cli, ["organize", str(messy), "--dry-run"])
    assert r.exit_code == 0, r.output
    assert snapshot(messy) == before, "--dry-run must not touch the disk."
    assert r.output.splitlines() == ["would move: README -> other/README", "would move: a.pdf -> documents/a.pdf",
                                     "would move: b.PNG -> images/b.PNG"], f"One 'would move' line per file, forward slashes. Got {r.output!r}"


def test_organize_moves(runner, messy):
    r = runner.invoke(cli, ["organize", str(messy), "-n"])
    assert r.exit_code == 0 and (messy / "a.pdf").exists(), "-n is the short form of --dry-run."
    r = runner.invoke(cli, ["organize", str(messy)])
    assert r.exit_code == 0, r.output
    assert "moved: a.pdf -> documents/a.pdf" in r.output.splitlines()
    assert (messy / "documents" / "a.pdf").read_bytes() == b"pdf"


def test_missing_folder_or_a_file_is_a_usage_error(runner, messy):
    r = runner.invoke(cli, ["organize", str(messy / "nope")])
    assert r.exit_code == 2 and "does not exist" in r.output, "click.Path(exists=True) refuses a missing folder with exit 2."
    r = runner.invoke(cli, ["organize", str(messy / "a.pdf")])
    assert r.exit_code == 2, "file_okay=False: a file is not a folder (exit 2)."


def test_undo_asks_first(runner, messy):
    runner.invoke(cli, ["organize", str(messy)])
    after = snapshot(messy)
    r = runner.invoke(cli, ["undo", str(messy)], input="n\n")
    assert r.exit_code == 1, "Answering no must abort with exit code 1 (click.confirmation_option)."
    assert "Put all moved files back?" in r.output, "Ask the question 'Put all moved files back?'."
    assert snapshot(messy) == after, "After 'no' nothing may change."


def test_undo_with_yes(runner, messy):
    before = snapshot(messy)
    runner.invoke(cli, ["organize", str(messy)])
    r = runner.invoke(cli, ["undo", str(messy), "--yes"])
    assert r.exit_code == 0, r.output
    assert "restored 3 file(s)" in r.output
    assert snapshot(messy) == before, "Undo with --yes restores the folder exactly (the library does it; call solution.undo)."


def test_commands_call_the_library(runner, messy, monkeypatch):
    calls = []

    def fake_plan(root):
        calls.append("plan")
        return [(root / "a.pdf", root / "documents" / "a.pdf")]

    def fake_apply(moves, root, dry_run=False):
        calls.append(("apply", dry_run))
        return moves

    monkeypatch.setattr(solution, "plan_moves", fake_plan)
    monkeypatch.setattr(solution, "apply_moves", fake_apply)
    r = runner.invoke(cli, ["organize", str(messy), "--dry-run"])
    assert r.exit_code == 0, r.output
    assert calls == ["plan", ("apply", True)], \
        "The command must call the SAME library functions (plan_moves, then apply_moves with dry_run): keep the CLI layer thin."
    assert r.output.strip() == "would move: a.pdf -> documents/a.pdf"


def test_as_a_real_program(messy):
    r = subprocess.run([sys.executable, solution.__file__, "organize", str(messy), "--dry-run"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and "would move: a.pdf -> documents/a.pdf" in r.stdout, f"End the file with: if __name__ == '__main__': cli(). stderr: {r.stderr}"
    r = subprocess.run([sys.executable, solution.__file__, "organize", str(messy / "nope")], capture_output=True, text=True, timeout=30)
    assert r.returncode == 2, "A missing folder is exit code 2 for the real program too."
