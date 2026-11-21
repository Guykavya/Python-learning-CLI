import json

import pytest

from solution import JOURNAL, apply_moves, plan_moves


def snapshot(root):
    """Every path under root, with the bytes of each file (None for folders)."""
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None) for p in sorted(root.rglob("*"))}


@pytest.fixture
def messy(tmp_path):
    for name, data in {"a.pdf": b"pdf", "b.PNG": b"png", "c": b"none", ".hidden": b"h"}.items():
        (tmp_path / name).write_bytes(data)
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "old.png").write_bytes(b"old")
    return tmp_path


def test_plan(messy):
    moves = plan_moves(messy)
    assert moves == [(messy / "a.pdf", messy / "documents" / "a.pdf"),
                     (messy / "b.PNG", messy / "images" / "b.PNG"),
                     (messy / "c", messy / "other" / "c")], \
        f"Files directly in root, sorted by name, no hidden files, no folders. Got {moves}"


def test_plan_changes_nothing(messy):
    before = snapshot(messy)
    plan_moves(messy)
    assert snapshot(messy) == before, "plan_moves only looks: no mkdir, no move, no journal."


def test_plan_never_overwrites(messy):
    (messy / "documents").mkdir()
    (messy / "documents" / "a.pdf").write_bytes(b"OLD")
    dst = dict(plan_moves(messy))[messy / "a.pdf"]
    assert dst == messy / "documents" / "a (1).pdf", "Use unique_destination: documents/a.pdf is taken."


def test_dry_run_changes_nothing(messy):
    before = snapshot(messy)
    moves = plan_moves(messy)
    result = apply_moves(moves, messy, dry_run=True)
    assert result == moves, "A dry run returns the moves it WOULD do."
    after = snapshot(messy)
    assert after == before, \
        f"A dry run must not touch the disk (no folders, no moves, no journal). New or changed: {sorted(set(after) ^ set(before))}"


def test_real_run_moves_and_keeps_contents(messy):
    apply_moves(plan_moves(messy), messy)
    assert (messy / "documents" / "a.pdf").read_bytes() == b"pdf"
    assert (messy / "images" / "b.PNG").read_bytes() == b"png", "b.PNG goes into the EXISTING images folder."
    assert (messy / "images" / "old.png").read_bytes() == b"old", "The file already in images/ must stay."
    assert (messy / "other" / "c").read_bytes() == b"none", "Create the category folder when it is missing."
    assert not (messy / "a.pdf").exists(), "The source is gone after a move."
    assert (messy / ".hidden").exists(), "Hidden files stay where they are."


def test_journal_lists_the_moves(messy):
    moves = plan_moves(messy)
    apply_moves(moves, messy)
    journal = messy / JOURNAL
    assert journal.exists(), f"After a real run, write the journal {JOURNAL} in root."
    data = json.loads(journal.read_text(encoding="utf-8"))
    assert data == [[str(s), str(d)] for s, d in moves], "The journal is a JSON list of [str(src), str(dst)] pairs, in move order."


def test_no_journal_when_nothing_moved(tmp_path):
    (tmp_path / ".only-hidden").write_bytes(b"x")
    assert apply_moves(plan_moves(tmp_path), tmp_path) == []
    assert not (tmp_path / JOURNAL).exists(), "Nothing moved: do not write a journal (it would replace the last real one)."


def test_second_run_has_nothing_to_do(messy):
    apply_moves(plan_moves(messy), messy)
    assert plan_moves(messy) == [], "After organizing, every file is in a folder and the journal is hidden: nothing to plan."
