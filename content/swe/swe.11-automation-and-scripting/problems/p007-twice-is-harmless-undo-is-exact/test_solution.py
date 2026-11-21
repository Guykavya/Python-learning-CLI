import subprocess
import sys

import pytest

import solution
from solution import JOURNAL, main, undo


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None) for p in sorted(root.rglob("*"))}


@pytest.fixture
def messy(tmp_path):
    for name, data in {"a.pdf": b"pdf", "b.PNG": b"png", "c": b"none", ".hidden": b"h"}.items():
        (tmp_path / name).write_bytes(data)
    return tmp_path


def test_dry_run_changes_nothing(messy, capsys):
    before = snapshot(messy)
    assert main(["organize", str(messy), "--dry-run"]) == 0
    assert snapshot(messy) == before, "A dry run must not touch the disk."
    out, err = capsys.readouterr()
    assert "would move: a.pdf -> documents/a.pdf" in out.splitlines(), f"One 'would move: NAME -> folder/NAME' line per file on stdout; got {out!r}"
    assert "3 file(s) to move" in err, f"The dry-run summary goes to stderr: '3 file(s) to move'. stderr: {err!r}"


def test_organize_prints_moves_and_summary(messy, capsys):
    assert main(["organize", str(messy)]) == 0
    out, err = capsys.readouterr()
    assert out.splitlines() == ["moved: a.pdf -> documents/a.pdf", "moved: b.PNG -> images/b.PNG", "moved: c -> other/c"], \
        f"stdout holds only the move lines, with forward slashes (as_posix). Got {out!r}"
    assert "3 file(s) moved" in err and "moved:" not in err


def test_running_twice_is_harmless(messy, capsys):
    main(["organize", str(messy)])
    after_first = snapshot(messy)
    capsys.readouterr()
    assert main(["organize", str(messy)]) == 0
    out, err = capsys.readouterr()
    assert "0 file(s) moved" in err, "The second run must find nothing to do."
    assert snapshot(messy) == after_first, "The second run must not change anything (the journal of the first run is kept too)."


def test_undo_restores_everything(messy, capsys):
    before = snapshot(messy)
    main(["organize", str(messy)])
    capsys.readouterr()
    assert main(["undo", str(messy)]) == 0
    assert capsys.readouterr().out.strip() == "restored 3 file(s)"
    assert snapshot(messy) == before, \
        "After undo the tree must be exactly as before: files back, empty category folders and the journal removed."


def test_undo_returns_pairs_and_removes_the_journal(messy):
    main(["organize", str(messy)])
    restored = undo(messy)
    assert sorted(s.name for d, s in restored) == ["a.pdf", "b.PNG", "c"], "Return (dst, src) pairs for what was restored."
    assert not (messy / JOURNAL).exists(), "Delete the journal after undo."
    assert undo(messy) == [], "Undo twice is harmless: no journal, nothing to do."


def test_undo_without_journal(tmp_path, capsys):
    (tmp_path / "x.txt").write_bytes(b"x")
    before = snapshot(tmp_path)
    assert main(["undo", str(tmp_path)]) == 0
    assert capsys.readouterr().out.strip() == "restored 0 file(s)"
    assert snapshot(tmp_path) == before


def test_undo_keeps_a_folder_that_has_other_files(tmp_path):
    (tmp_path / "documents").mkdir()
    (tmp_path / "documents" / "a.pdf").write_bytes(b"OLD")
    (tmp_path / "a.pdf").write_bytes(b"NEW")
    main(["organize", str(tmp_path)])
    assert (tmp_path / "documents" / "a (1).pdf").read_bytes() == b"NEW"
    undo(tmp_path)
    assert (tmp_path / "a.pdf").read_bytes() == b"NEW", "The renamed file 'a (1).pdf' goes back to its original name a.pdf."
    assert (tmp_path / "documents" / "a.pdf").read_bytes() == b"OLD", \
        "documents/ held a file before: keep the folder and its file (rmdir only removes empty folders)."


def test_undo_never_overwrites_a_new_file(messy):
    main(["organize", str(messy)])
    (messy / "a.pdf").write_bytes(b"made after organize")
    undo(messy)
    assert (messy / "a.pdf").read_bytes() == b"made after organize", "A file now sitting at the source must not be overwritten."
    assert (messy / "documents" / "a.pdf").read_bytes() == b"pdf", "...so the moved copy stays where it is."


def test_missing_folder_is_exit_code_1(tmp_path, capsys):
    assert main(["organize", str(tmp_path / "nope")]) == 1
    out, err = capsys.readouterr()
    assert "not a folder" in err and out == "", "Error to stderr, nothing on stdout, exit 1."
    assert main(["undo", str(tmp_path / "nope")]) == 1


def test_usage_error_is_exit_code_2():
    with pytest.raises(SystemExit) as e:
        main(["organise", "x"])
    assert e.value.code == 2


def test_as_a_real_program(messy):
    r = subprocess.run([sys.executable, solution.__file__, "organize", str(messy), "-n"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and "would move: a.pdf -> documents/a.pdf" in r.stdout, f"Real program, dry run. stderr: {r.stderr}"
    r = subprocess.run([sys.executable, solution.__file__, "undo", str(messy / "nope")], capture_output=True, text=True, timeout=30)
    assert r.returncode == 1, "Keep sys.exit(main()) so the exit code reaches the shell."
