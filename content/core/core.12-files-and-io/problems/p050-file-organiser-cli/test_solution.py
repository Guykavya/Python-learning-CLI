import os
import shutil
from datetime import datetime

import pytest

from solution import main


# ------------------------------------------------------------------ helpers

def make_messy(root):
    """A messy folder. Every file has its own content, so a mix-up is easy to see."""
    files = {
        "photo.JPG": "p", "notes.txt": "n", "report.pdf": "r", "data.csv": "d",
        "script.py": "s", "archive.zip": "a", "README": "readme", ".hidden": "h",
        "sub/inner.txt": "inner",
    }
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def snapshot(root):
    """Every file and folder under root, with the content of the files."""
    return {p.relative_to(root).as_posix(): (p.read_text(encoding="utf-8") if p.is_file() else None)
            for p in root.rglob("*")}


def run(capsys, *args):
    code = main([str(a) for a in args])
    shown = capsys.readouterr()
    return code, shown.out, shown.err


# ------------------------------------------------------------------ by type

def test_by_type_default(tmp_path, capsys):
    root = make_messy(tmp_path / "messy")
    code, out, err = run(capsys, root)
    assert code == 0, "A normal run returns exit code 0."
    expected = {
        "images/photo.JPG": "p", "documents/notes.txt": "n", "documents/report.pdf": "r",
        "data/data.csv": "d", "code/script.py": "s", "archives/archive.zip": "a", "other/README": "readme",
        ".hidden": "h", "sub/inner.txt": "inner",
    }
    files = {k: v for k, v in snapshot(root).items() if v is not None}
    assert files == expected, "Move each top-level file into the folder of its type. The extension is case-insensitive (.JPG is an image), files without a known extension go to 'other', hidden files (names starting with a dot) and sub-folders stay where they are."


def test_summary_output(tmp_path, capsys):
    root = make_messy(tmp_path / "messy")
    code, out, err = run(capsys, root)
    lines = out.splitlines()
    assert lines[-1] == "moved 7 files", "The last line is the summary: 'moved 7 files'."
    assert "moved README -> other/README" in lines, "Each move prints 'moved NAME -> FOLDER/NAME' (path relative to dest, with /)."
    assert lines[:-1] == sorted(lines[:-1], key=lambda l: l.split()[1]), "Print the moves in the order of the file names (plain string sort)."
    assert err == "", "Nothing goes to stderr in a normal run."


def test_single_file_summary_is_singular(tmp_path, capsys):
    root = tmp_path / "one"
    root.mkdir()
    (root / "a.txt").write_text("a")
    code, out, err = run(capsys, root)
    assert out.splitlines()[-1] == "moved 1 file", "Use 'file' (not 'files') when the count is 1."


# ------------------------------------------------------------------ never overwrite

def test_never_overwrites_existing_file(tmp_path, capsys):
    root = make_messy(tmp_path / "messy")
    (root / "documents").mkdir()
    (root / "documents" / "notes.txt").write_text("OLD", encoding="utf-8")
    run(capsys, root)
    assert (root / "documents" / "notes.txt").read_text(encoding="utf-8") == "OLD", "An existing file must never be overwritten."
    assert (root / "documents" / "notes_1.txt").read_text(encoding="utf-8") == "n", "The new file gets a numeric suffix: notes_1.txt."


def test_suffix_counts_up(tmp_path, capsys):
    root = make_messy(tmp_path / "messy")
    (root / "documents").mkdir()
    (root / "documents" / "notes.txt").write_text("OLD0", encoding="utf-8")
    (root / "documents" / "notes_1.txt").write_text("OLD1", encoding="utf-8")
    code, out, _ = run(capsys, root)
    assert (root / "documents" / "notes_2.txt").read_text(encoding="utf-8") == "n", "If notes_1.txt exists too, use notes_2.txt."
    assert "moved notes.txt -> documents/notes_2.txt" in out.splitlines(), "The printed line shows the real new name."


def test_name_clash_inside_one_run(tmp_path, capsys):
    root = tmp_path / "clash"
    (root / "documents").mkdir(parents=True)
    (root / "documents" / "a.txt").write_text("old", encoding="utf-8")
    (root / "a.txt").write_text("first", encoding="utf-8")
    (root / "a_1.txt").write_text("second", encoding="utf-8")
    run(capsys, root)
    got = {p.name: p.read_text(encoding="utf-8") for p in (root / "documents").iterdir()}
    assert got == {"a.txt": "old", "a_1.txt": "first", "a_1_1.txt": "second"}, "'a.txt' takes the free name a_1.txt. Then 'a_1.txt' finds its own name taken and becomes a_1_1.txt. No content may be lost."


# ------------------------------------------------------------------ dry run

def test_dry_run_changes_nothing(tmp_path, capsys):
    root = make_messy(tmp_path / "messy")
    before = snapshot(root)
    code, out, err = run(capsys, root, "--dry-run")
    assert code == 0, "A dry run returns 0."
    assert snapshot(root) == before, "A dry run must not move, create or delete anything (also no empty folders)."
    lines = out.splitlines()
    assert lines[-1] == "would move 7 files", "The dry-run summary says 'would move 7 files'."
    assert "would move photo.JPG -> images/photo.JPG" in lines, "Each planned move prints 'would move NAME -> FOLDER/NAME'."
    assert not any(l.startswith("moved") for l in lines), "A dry run never says 'moved'."


def test_dry_run_matches_real_run(tmp_path, capsys):
    root = tmp_path / "clash"
    (root / "documents").mkdir(parents=True)
    (root / "documents" / "a.txt").write_text("old")
    (root / "a.txt").write_text("1")
    (root / "a_1.txt").write_text("2")
    (root / "b.txt").write_text("3")
    _, dry, _ = run(capsys, root, "--dry-run")
    _, real, _ = run(capsys, root)
    assert dry.replace("would move", "moved") == real, "The dry run must predict exactly what the real run does, including renamed targets. Keep a set of the names you have already planned."


def test_dry_run_with_dest_creates_no_folder(tmp_path, capsys):
    root = make_messy(tmp_path / "messy")
    dest = tmp_path / "out"
    run(capsys, root, "--dry-run", "--dest", dest)
    assert not dest.exists(), "A dry run must not create the destination folder."


# ------------------------------------------------------------------ dest

def test_dest_folder(tmp_path, capsys):
    root = make_messy(tmp_path / "messy")
    dest = tmp_path / "sorted"
    code, out, _ = run(capsys, root, "--dest", dest)
    assert code == 0, "A run with --dest returns 0."
    assert (dest / "images" / "photo.JPG").read_text(encoding="utf-8") == "p", "With --dest the sub-folders are made inside dest (dest is created if needed)."
    assert not (root / "images").exists(), "Nothing is created in the source folder when --dest is used."
    assert not (root / "notes.txt").exists(), "The files leave the source folder."
    assert (root / ".hidden").exists() and (root / "sub" / "inner.txt").exists(), "Hidden files and sub-folders stay."


def test_dest_existing_folder_with_clash(tmp_path, capsys):
    root = tmp_path / "src"
    root.mkdir()
    (root / "a.csv").write_text("new")
    dest = tmp_path / "dst"
    (dest / "data").mkdir(parents=True)
    (dest / "data" / "a.csv").write_text("old")
    run(capsys, root, "--dest", dest)
    assert (dest / "data" / "a.csv").read_text() == "old", "Never overwrite files in dest."
    assert (dest / "data" / "a_1.csv").read_text() == "new", "The new file is renamed with a numeric suffix."


# ------------------------------------------------------------------ by date

def test_by_date(tmp_path, capsys):
    root = tmp_path / "dates"
    root.mkdir()
    for name, when in [("a.txt", datetime(2024, 3, 15, 12, 0)), ("b.txt", datetime(2023, 12, 10, 12, 0)),
                       ("c.txt", datetime(2024, 3, 20, 12, 0))]:
        (root / name).write_text(name)
        stamp = when.timestamp()
        os.utime(root / name, (stamp, stamp))
    run(capsys, root, "--by", "date")
    found = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    assert found == {"2024-03/a.txt", "2023-12/b.txt", "2024-03/c.txt"}, "With --by date the folder is the modification month as YYYY-MM (use st_mtime and datetime.fromtimestamp(...).strftime('%Y-%m'))."


# ------------------------------------------------------------------ by size

def test_by_size(tmp_path, capsys):
    root = tmp_path / "sizes"
    root.mkdir()
    sizes = {"tiny": 10, "edge_small": 1023, "edge_medium": 1024, "mid": 5000, "edge_mid_top": 102399,
             "edge_large": 102400, "big": 200000}
    for name, size in sizes.items():
        (root / f"{name}.bin").write_bytes(b"x" * size)
    run(capsys, root, "--by", "size")
    where = {p.name: p.parent.name for p in root.rglob("*") if p.is_file()}
    assert where == {
        "tiny.bin": "small", "edge_small.bin": "small", "edge_medium.bin": "medium", "mid.bin": "medium",
        "edge_mid_top.bin": "medium", "edge_large.bin": "large", "big.bin": "large",
    }, "small: under 1024 bytes. medium: from 1024 up to 102399 bytes. large: 102400 bytes or more."


# ------------------------------------------------------------------ errors and exit codes

def test_missing_source(tmp_path, capsys):
    code, out, err = run(capsys, tmp_path / "nope")
    assert code == 2, "A source folder that does not exist gives exit code 2."
    assert out == "" and err.startswith("error:"), "Print 'error: ...' to stderr, and nothing to stdout."
    assert list(tmp_path.iterdir()) == [], "Nothing may be created."


def test_source_is_a_file(tmp_path, capsys):
    f = tmp_path / "file.txt"
    f.write_text("x")
    code, out, err = run(capsys, f)
    assert code == 2 and err.startswith("error:"), "A source that is a file (not a folder) is also an error with exit code 2."


def test_dest_is_a_file(tmp_path, capsys):
    root = make_messy(tmp_path / "messy")
    bad = tmp_path / "afile"
    bad.write_text("x")
    before = snapshot(root)
    code, out, err = run(capsys, root, "--dest", bad)
    assert code == 2 and err.startswith("error:"), "A destination that is a file is an error with exit code 2."
    assert snapshot(root) == before, "Check the arguments before you move anything."


def test_bad_arguments_exit_2(tmp_path):
    with pytest.raises(SystemExit) as info:
        main([str(tmp_path), "--by", "colour"])
    assert info.value.code == 2, "--by accepts only type, date or size (choices=...). argparse exits with 2."
    with pytest.raises(SystemExit) as info:
        main([])
    assert info.value.code == 2, "The source folder is required."


def test_partial_failure_returns_1(tmp_path, capsys, monkeypatch):
    root = make_messy(tmp_path / "messy")
    real_move = shutil.move

    def flaky_move(src, dst, *args, **kwargs):
        if os.path.basename(src) == "notes.txt":
            raise OSError("disk says no")
        return real_move(src, dst, *args, **kwargs)

    monkeypatch.setattr(shutil, "move", flaky_move)
    code, out, err = run(capsys, root)
    assert code == 1, "If a move fails, go on with the other files and return exit code 1 at the end. Use shutil.move and catch OSError."
    assert (root / "notes.txt").read_text(encoding="utf-8") == "n", "The file that failed stays in place."
    assert (root / "images" / "photo.JPG").exists(), "The other files are still moved."
    assert "notes.txt" in err, "Name the file that failed on stderr."
    assert out.splitlines()[-1] == "moved 6 files", "The summary counts only the files that were moved."


# ------------------------------------------------------------------ idempotent, empty

def test_second_run_is_a_no_op(tmp_path, capsys):
    root = make_messy(tmp_path / "messy")
    run(capsys, root)
    after_first = snapshot(root)
    code, out, err = run(capsys, root)
    assert code == 0, "A second run is not an error."
    assert out == "nothing to do\n", "Nothing is left in the top level, so print 'nothing to do'."
    assert snapshot(root) == after_first, "A second run must change nothing (no renamed copies, no new folders)."


def test_second_run_with_dest_is_a_no_op(tmp_path, capsys):
    root = make_messy(tmp_path / "messy")
    dest = tmp_path / "sorted"
    run(capsys, root, "--dest", dest)
    before = snapshot(tmp_path)
    code, out, _ = run(capsys, root, "--dest", dest)
    assert (code, out) == (0, "nothing to do\n"), "The source has no files left, so there is nothing to do."
    assert snapshot(tmp_path) == before, "Nothing changes."


def test_empty_folder(tmp_path, capsys):
    root = tmp_path / "empty"
    root.mkdir()
    code, out, err = run(capsys, root)
    assert (code, out) == (0, "nothing to do\n"), "An empty folder: print 'nothing to do', return 0."
    assert list(root.iterdir()) == [], "Do not create sub-folders when there is nothing to move."


def test_only_hidden_and_folders(tmp_path, capsys):
    root = tmp_path / "quiet"
    (root / "dir").mkdir(parents=True)
    (root / ".env").write_text("secret")
    before = snapshot(root)
    code, out, _ = run(capsys, root)
    assert (code, out) == (0, "nothing to do\n"), "Hidden files and folders are not moved, so there is nothing to do."
    assert snapshot(root) == before, "Nothing changes."


def test_content_is_preserved_for_large_files(tmp_path, capsys):
    root = tmp_path / "bin"
    root.mkdir()
    data = bytes(range(256)) * 800
    (root / "blob.dat").write_bytes(data)
    run(capsys, root)
    assert (root / "other" / "blob.dat").read_bytes() == data, "The bytes of a moved file must be exactly the same."
