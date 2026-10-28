import struct

import pytest

from solution import HEADER, MAGIC, RECORD, pack_header, pack_record, read_file, unpack_header, unpack_record, write_file


def test_formats_have_no_padding():
    assert struct.calcsize(HEADER) == 20 and struct.calcsize(RECORD) == 20, (
        "Both formats must be 20 bytes: start them with '<' (without it, native alignment adds padding: 24 bytes)."
    )
    assert MAGIC == b"KVLG", "MAGIC is the bytes b'KVLG'."


def test_pack_header_exact_bytes():
    data = pack_header(1, 3, 2, 1700000000)
    assert isinstance(data, bytes) and len(data) == 20, "pack_header returns 20 bytes."
    assert data.hex(" ") == "4b 56 4c 47 01 00 03 00 02 00 00 00 00 f1 53 65 00 00 00 00", (
        "Expected magic, then version, flags, count, timestamp in LITTLE-endian ('<4sHHIq'). "
        "Bytes in reverse order mean you used '>'."
    )


def test_unpack_header_roundtrip():
    header = unpack_header(pack_header(2, 65535, 4_000_000_000, -5))
    assert header == {"version": 2, "flags": 65535, "count": 4_000_000_000, "timestamp": -5}, (
        "unpack_header returns a dict with version, flags, count, timestamp (not the magic). "
        "H holds up to 65535, I up to 4294967295, q is signed."
    )


def test_unpack_header_ignores_extra_bytes():
    data = pack_header(1, 0, 0, 0) + b"more data"
    assert unpack_header(data)["version"] == 1, "Only the first 20 bytes are the header: slice data[:20] before unpacking."


def test_unpack_header_errors():
    with pytest.raises(ValueError):
        unpack_header(b"KVLG\x01\x00")          # too short
    with pytest.raises(ValueError):
        unpack_header(b"PNG!" + pack_header(1, 0, 0, 0)[4:])   # wrong magic


def test_pack_header_out_of_range():
    with pytest.raises(struct.error):
        pack_header(1, 0, -1, 0)                # count is unsigned


def test_pack_record_exact_bytes():
    data = pack_record(7, 2.5, "pen")
    assert data.hex(" ") == "07 00 00 00 00 00 00 00 00 00 04 40 70 65 6e 00 00 00 00 00", (
        "Record = '<Id8s': id as 4 bytes little-endian, value as an 8-byte float, the name padded to 8 bytes with \\x00."
    )


def test_record_roundtrip():
    assert unpack_record(pack_record(7, 2.5, "pen")) == (7, 2.5, "pen"), "Strip the \\x00 padding and decode the name."
    assert unpack_record(pack_record(0, -1e-3, "")) == (0, -1e-3, ""), "An empty name comes back as ''."
    assert unpack_record(pack_record(4294967295, 0.0, "café")) == (4294967295, 0.0, "café"), "'café' is 5 UTF-8 bytes: it fits."


def test_record_name_too_long():
    with pytest.raises(ValueError):
        pack_record(1, 1.0, "notebook9")        # 9 bytes: struct would silently cut it to 'notebook'
    with pytest.raises(ValueError):
        pack_record(1, 1.0, "ññññð")             # 5 characters but 10 bytes: count BYTES, not characters
    assert unpack_record(pack_record(1, 1.0, "notebook"))[2] == "notebook", "Exactly 8 bytes is allowed."


def test_record_negative_id():
    with pytest.raises(struct.error):
        pack_record(-1, 1.0, "x")


def test_write_and_read_file(tmp_path):
    path = tmp_path / "data.kvlg"
    records = [(1, 9.5, "pen"), (2, 0.25, "ink"), (3, -4.0, "café")]
    write_file(path, records, timestamp=1735689600, version=2, flags=1)
    raw = path.read_bytes()
    assert len(raw) == 20 + 3 * 20, "The file is one 20-byte header plus 20 bytes per record."
    assert raw[:4] == b"KVLG", "The file starts with the magic bytes."
    header, back = read_file(path)
    assert header == {"version": 2, "flags": 1, "count": 3, "timestamp": 1735689600}, "count in the header is len(records)."
    assert back == records, "read_file must return the same (id, value, name) tuples that were written."


def test_write_read_empty(tmp_path):
    path = tmp_path / "empty.kvlg"
    write_file(path, [], timestamp=0)
    header, back = read_file(path)
    assert header["count"] == 0 and back == [], "No records: a header with count 0 and an empty list."
    assert header["version"] == 1 and header["flags"] == 0, "version defaults to 1 and flags to 0."


def test_read_truncated_file(tmp_path):
    path = tmp_path / "cut.kvlg"
    write_file(path, [(1, 1.0, "a"), (2, 2.0, "b")], timestamp=0)
    path.write_bytes(path.read_bytes()[:-5])
    with pytest.raises(ValueError):
        read_file(path)


def test_read_count_mismatch(tmp_path):
    path = tmp_path / "lie.kvlg"
    path.write_bytes(pack_header(1, 0, 3, 0) + pack_record(1, 1.0, "a"))
    with pytest.raises(ValueError):
        read_file(path)                         # header promises 3 records, the file has 1
