import zipfile
from pathlib import Path

import pytest

from solution import list_zip, read_member, safe_extract, zip_folder


def make(base: Path, rel: str, data: bytes):
    path = base / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    make(root, "readme.md", b"# Project\n")
    make(root, "src/main.py", b'print("hi")\n')
    make(root, "src/util/helpers.py", b"def h():\n    return 1\n" * 50)
    (root / "empty_dir").mkdir()
    return root


EXPECTED = ["readme.md", "src/main.py", "src/util/helpers.py"]


def test_zip_folder_names(project, tmp_path):
    out = tmp_path / "out" / "project.zip"
    names = zip_folder(project, out)
    assert names == EXPECTED, (
        "Member names are paths relative to src with '/' (use relative_to(src).as_posix() as arcname), sorted; "
        "folders are not members."
    )
    assert out.exists(), "zip_folder must create dest_zip (and its parent folder if needed)."


def test_zip_member_names_are_clean(project, tmp_path):
    out = tmp_path / "p.zip"
    zip_folder(project, out)
    with zipfile.ZipFile(out) as zf:
        stored = sorted(zf.namelist())
    assert stored == EXPECTED, "The archive itself must contain exactly these names (no absolute paths, no folder entries)."
    assert not any("\\" in n or n.startswith("/") or ":" in n for n in stored), "Names inside a zip use '/', never '\\' or a drive."


def test_zip_is_compressed(project, tmp_path):
    out = tmp_path / "p.zip"
    zip_folder(project, out)
    with zipfile.ZipFile(out) as zf:
        info = zf.getinfo("src/util/helpers.py")
    assert info.compress_type == zipfile.ZIP_DEFLATED, "Pass compression=zipfile.ZIP_DEFLATED: the default ZIP_STORED does not compress."
    assert info.compress_size < info.file_size, "A repetitive file must get smaller when deflated."


def test_zip_inside_src_not_added_to_itself(project):
    out = project / "backup.zip"
    names = zip_folder(project, out)
    assert "backup.zip" not in names, "dest_zip lies inside src: skip it, or the archive tries to contain itself."
    assert names == EXPECTED, "All the other files are still added."


def test_list_zip(project, tmp_path):
    out = tmp_path / "p.zip"
    zip_folder(project, out)
    assert list_zip(out) == EXPECTED, "list_zip returns the sorted file names of the archive."


def test_list_zip_skips_folder_entries(tmp_path):
    out = tmp_path / "dirs.zip"
    with zipfile.ZipFile(out, "w") as zf:
        zf.writestr("b.txt", "b")
        zf.writestr("docs/", "")
        zf.writestr("docs/a.txt", "a")
    assert list_zip(out) == ["b.txt", "docs/a.txt"], "Names ending in '/' are folder entries: leave them out."


def test_read_member(project, tmp_path):
    out = tmp_path / "p.zip"
    zip_folder(project, out)
    assert read_member(out, "src/main.py") == b'print("hi")\n', "read_member returns the member's bytes (ZipFile.read)."
    with pytest.raises(KeyError):
        read_member(out, "nope.txt")


def test_safe_extract_roundtrip(project, tmp_path):
    out = tmp_path / "p.zip"
    zip_folder(project, out)
    dest = tmp_path / "restored"
    assert safe_extract(out, dest) == EXPECTED, "safe_extract returns the sorted file names it extracted."
    for rel in EXPECTED:
        assert (dest / rel).read_bytes() == (project / rel).read_bytes(), f"{rel} must be restored with identical bytes."


@pytest.mark.parametrize("bad", ["../evil.txt", "a/../../evil.txt", "/abs.txt", "\\win.txt", "dir\\..\\evil.txt", "C:/evil.txt"])
def test_safe_extract_refuses_unsafe(tmp_path, bad):
    archive = tmp_path / "evil.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("good.txt", "fine")
        zf.writestr(bad, "evil")
    dest = tmp_path / "target"
    with pytest.raises(ValueError):
        safe_extract(archive, dest)
    assert not (dest / "good.txt").exists(), "Check ALL names before extracting anything: nothing may be written."
    assert not (tmp_path / "evil.txt").exists(), "Nothing may be written outside the target folder."


def test_safe_names_with_dots_are_fine(tmp_path):
    archive = tmp_path / "ok.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("..hidden/x.txt", "1")
        zf.writestr("v1..2/notes.txt", "2")
    assert safe_extract(archive, tmp_path / "t") == ["..hidden/x.txt", "v1..2/notes.txt"], (
        "Only a path PART equal to '..' is dangerous; '..hidden' or 'v1..2' are ordinary names. Check parts, not substrings."
    )
