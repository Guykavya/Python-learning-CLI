import pytest

from solution import copy_project


def make(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_text(encoding="utf-8") if p.is_file() else None) for p in root.rglob("*")}


def test_example_with_copyignore(tmp_path):
    src = tmp_path / "src"
    make(src, {
        "app.py": "print(1)", "data/notes.log": "log", "pkg/__pycache__/x.pyc": "bin",
        "pkg/mod.py": "m", ".copyignore": "# junk\n*.log\n",
    })
    result = copy_project(src, tmp_path / "dst")
    assert result == [".copyignore", "app.py", "pkg/mod.py"], "Skip __pycache__ and *.pyc (defaults) and *.log (from .copyignore). Return sorted relative file paths."
    assert (tmp_path / "dst" / "data").is_dir(), "The folder data is copied, only the .log file inside is skipped."
    assert (tmp_path / "dst" / "app.py").read_text(encoding="utf-8") == "print(1)", "Files keep their content."


def test_source_unchanged(tmp_path):
    src = tmp_path / "src"
    make(src, {"a.py": "a", "__pycache__/a.pyc": "x", "sub/b.txt": "b"})
    before = snapshot(src)
    copy_project(src, tmp_path / "dst")
    assert snapshot(src) == before, "The source folder must not change."


def test_ignored_at_any_depth(tmp_path):
    src = tmp_path / "src"
    make(src, {"a/b/c/__pycache__/z.pyc": "x", "a/b/c/keep.py": "k", "a/.git/config": "g", "top.pyc": "t"})
    assert copy_project(src, tmp_path / "dst") == ["a/b/c/keep.py"], "Patterns match names at every depth, for files and for folders."


def test_custom_ignore_argument(tmp_path):
    src = tmp_path / "src"
    make(src, {"a.txt": "a", "b.tmp": "b", "build/out.bin": "o"})
    result = copy_project(src, tmp_path / "dst", ignore=("*.tmp", "build"))
    assert result == ["a.txt"], "The ignore argument replaces the default patterns."


def test_copyignore_comments_blank_and_spaces(tmp_path):
    src = tmp_path / "src"
    make(src, {"a.txt": "a", "x.bak": "x", "y.old": "y", ".copyignore": "# comment\n\n   *.bak   \n*.old\n"})
    result = copy_project(src, tmp_path / "dst", ignore=())
    assert result == [".copyignore", "a.txt"], "Skip empty lines and lines that start with #. Strip spaces around the patterns."


def test_existing_destination_raises(tmp_path):
    src = tmp_path / "src"
    make(src, {"a.txt": "new"})
    dst = tmp_path / "dst"
    make(dst, {"a.txt": "old", "extra.txt": "e"})
    before = snapshot(dst)
    with pytest.raises(FileExistsError):
        copy_project(src, dst)
    assert snapshot(dst) == before, "If dst exists and overwrite is False, nothing may change."


def test_overwrite_merges(tmp_path):
    src = tmp_path / "src"
    make(src, {"a.txt": "new", "sub/b.txt": "b", "c.pyc": "x"})
    dst = tmp_path / "dst"
    make(dst, {"a.txt": "old", "extra.txt": "e"})
    result = copy_project(src, dst, overwrite=True)
    assert (dst / "a.txt").read_text(encoding="utf-8") == "new", "With overwrite=True the old file is replaced (dirs_exist_ok=True)."
    assert result == ["a.txt", "extra.txt", "sub/b.txt"], "The result lists every file in dst afterwards, also the one that was there before."


def test_dst_inside_new_parent(tmp_path):
    src = tmp_path / "src"
    make(src, {"a.txt": "a"})
    assert copy_project(src, tmp_path / "deep" / "er" / "dst") == ["a.txt"], "copytree creates the missing parent folders of dst."


def test_returns_strings_and_only_files(tmp_path):
    src = tmp_path / "src"
    make(src, {"a/b.txt": "b"})
    (src / "empty").mkdir()
    result = copy_project(src, tmp_path / "dst")
    assert result == ["a/b.txt"], "List only files. Empty folders and folders are not in the result."
    assert all(isinstance(r, str) for r in result), "Return str, not Path (use as_posix())."
