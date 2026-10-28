import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from solution import archive_formats, archive_members, make_backup, restore

FILES = {"a.txt": b"alpha\n", "sub/b.txt": b"beta\n", "sub/deep/c.bin": bytes(range(256))}


@pytest.fixture
def src(tmp_path):
    root = tmp_path / "src"
    for rel, data in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return root


def test_archive_formats():
    formats = archive_formats()
    assert isinstance(formats, list) and formats == sorted(formats), "Return a sorted list of format NAMES (strings)."
    assert {"zip", "tar", "gztar"} <= set(formats), "zip, tar and gztar are always available: take the names from shutil.get_archive_formats()."


def test_make_backup_zip(src, tmp_path):
    out = tmp_path / "out"
    path = make_backup(src, out, "bk")
    assert isinstance(path, Path), "Return a pathlib.Path (make_archive returns a str)."
    assert path.name == "bk.zip", "base_name has no extension; make_archive adds '.zip'. 'bk.zip.zip' means you added it twice."
    assert path.exists() and path.parent == out, "The archive goes into out_dir (create it if needed)."


def test_make_backup_gztar(src, tmp_path):
    path = make_backup(src, tmp_path / "out", "bk", "gztar")
    assert path.name == "bk.tar.gz", "gztar archives end in .tar.gz."
    assert tarfile.is_tarfile(path), "The file must really be a tar archive."


def test_make_backup_unknown_format(src, tmp_path):
    with pytest.raises(ValueError):
        make_backup(src, tmp_path / "out", "bk", "rar")


def test_members_zip(src, tmp_path):
    path = make_backup(src, tmp_path / "out", "bk", "zip")
    assert archive_members(path) == sorted(FILES), (
        "Only files, sorted, relative to src: make_archive adds folder entries like 'sub/' to zips; skip names ending in '/'."
    )


@pytest.mark.parametrize("fmt", ["tar", "gztar"])
def test_members_tar(src, tmp_path, fmt):
    path = make_backup(src, tmp_path / "out", "bk", fmt)
    assert archive_members(path) == sorted(FILES), (
        "Tar names from make_archive start with './' and include folders: keep only members that are files "
        "(member.isfile()) and remove the leading './'."
    )


def test_members_not_an_archive(tmp_path):
    junk = tmp_path / "notes.txt"
    junk.write_text("just text", encoding="utf-8")
    with pytest.raises(ValueError):
        archive_members(junk)


@pytest.mark.parametrize("fmt", ["zip", "gztar"])
def test_roundtrip(src, tmp_path, fmt):
    path = make_backup(src, tmp_path / "out", "bk", fmt)
    dest = tmp_path / f"restored-{fmt}"
    assert restore(path, dest) == sorted(FILES), "restore returns the sorted relative paths (with '/') of the files under dest."
    for rel, data in FILES.items():
        assert (dest / rel).read_bytes() == data, f"{rel} must come back byte for byte."


def test_restore_tar_refuses_escape(tmp_path):
    archive = tmp_path / "evil.tar"
    with tarfile.open(archive, "w") as tf:
        data = b"evil"
        info = tarfile.TarInfo("../escaped.txt")
        info.size = len(data)
        tf.addfile(info, io.BytesIO(data))
    with pytest.raises(tarfile.TarError):
        restore(archive, tmp_path / "dest")
    assert not (tmp_path / "escaped.txt").exists(), "Pass filter='data' when unpacking tar archives: it refuses members that leave dest."


def test_restore_hand_made_zip(tmp_path):
    archive = tmp_path / "hand.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("x/y.txt", "y")
        zf.writestr("z.txt", "z")
    assert archive_members(archive) == ["x/y.txt", "z.txt"], "archive_members works for any zip, not just ones you made."
    assert restore(archive, tmp_path / "d") == ["x/y.txt", "z.txt"], "restore must work for zip files (no filter argument for zips)."
