import builtins
import io

import pytest

from solution import copy_blocks


def make(tmp_path, data):
    p = tmp_path / "src.bin"
    p.write_bytes(data)
    return p


def test_ten_bytes_block_four(tmp_path):
    src = make(tmp_path, bytes(range(10)))
    dst = tmp_path / "dst.bin"
    assert copy_blocks(src, dst, 4) == 3, "10 bytes in blocks of 4 are 3 blocks (4 + 4 + 2)."
    assert dst.read_bytes() == bytes(range(10)), "The copy must be identical, byte for byte."


def test_not_text(tmp_path):
    data = b"\xff\xfe\x00\r\n\x80abc\r\n\x00"
    src = make(tmp_path, data)
    dst = tmp_path / "dst.bin"
    copy_blocks(str(src), str(dst), 3)
    assert dst.read_bytes() == data, "Use binary mode ('rb' and 'wb'). Text mode changes line endings and fails on bad UTF-8."


def test_exact_multiple(tmp_path):
    src = make(tmp_path, b"x" * 8)
    assert copy_blocks(src, tmp_path / "d", 4) == 2, "8 bytes in blocks of 4 are exactly 2 blocks, not 3."


def test_empty_file(tmp_path):
    src = make(tmp_path, b"")
    dst = tmp_path / "dst.bin"
    assert copy_blocks(src, dst, 4) == 0, "An empty file has 0 blocks. Do not count the empty read at the end."
    assert dst.exists() and dst.read_bytes() == b"", "dst must be created, empty."


def test_overwrites_dst(tmp_path):
    src = make(tmp_path, b"new")
    dst = tmp_path / "dst.bin"
    dst.write_bytes(b"old old old old")
    copy_blocks(src, dst, 2)
    assert dst.read_bytes() == b"new", "Open dst with 'wb' so old content is replaced."


def test_block_size_one(tmp_path):
    src = make(tmp_path, b"abcde")
    assert copy_blocks(src, tmp_path / "d", 1) == 5, "Block size 1 on 5 bytes means 5 blocks."


def test_never_reads_more_than_a_block(tmp_path, monkeypatch):
    src = make(tmp_path, b"z" * 5000)
    sizes = []
    real_open = io.open

    class Spy:
        def __init__(self, f):
            self._f = f

        def __enter__(self):
            self._f.__enter__()
            return self

        def __exit__(self, *a):
            return self._f.__exit__(*a)

        def read(self, size=-1):
            sizes.append(size)
            return self._f.read(size)

        def __getattr__(self, name):
            return getattr(self._f, name)

    monkeypatch.setattr(builtins, "open", lambda *a, **k: Spy(real_open(*a, **k)))
    dst = tmp_path / "out.bin"
    assert copy_blocks(src, dst, 1000) == 5, "5000 bytes in blocks of 1000 are 5 blocks."
    assert sizes and all(0 < s <= 1000 for s in sizes), "Call read(block_size) every time. read() with no size loads the whole file."
    assert dst.read_bytes() == b"z" * 5000, "The copy must be identical."
