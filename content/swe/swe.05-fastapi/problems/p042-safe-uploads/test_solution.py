import pytest
from fastapi.testclient import TestClient
from starlette.datastructures import UploadFile

from solution import app

MAX = 1024 * 1024


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def send(client, name, content, ctype="text/csv"):
    return client.post("/upload", files={"file": (name, content, ctype)})


def test_counts_data_rows(client):
    r = send(client, "tasks.csv", b"id,title\n1,write\n2,test\n")
    assert r.status_code == 200, f"A small CSV must be accepted, got {r.status_code} {r.text}"
    assert r.json() == {"filename": "tasks.csv", "rows": 2}, (
        f"Two data rows after the header, got {r.json()}. Do not count the header.")


def test_header_only_and_no_final_newline(client):
    assert send(client, "h.csv", b"id,title\n").json()["rows"] == 0, "A header-only file has 0 rows."
    assert send(client, "n.csv", b"id,title\n1,a\n2,b").json()["rows"] == 2, (
        "The last row has no newline after it, and it still counts. Counting '\\n' gets this wrong; use csv.reader.")


def test_quoted_newlines_and_blank_lines(client):
    r = send(client, "notes.csv", b'id,title\n1,"two\nlines"\n\n2,x\n')
    assert r.json()["rows"] == 2, (
        f"Expected 2 rows (one value spans two lines, and one line is blank), got {r.json()['rows']}. "
        "Parse with csv.reader and skip empty rows.")


@pytest.mark.parametrize("ctype", ["image/png", "application/octet-stream", "text/plain"])
def test_wrong_type_is_415(client, ctype):
    r = send(client, "tasks.csv", b"id\n1\n", ctype)
    assert r.status_code == 415, f"content_type {ctype!r} must be refused with 415 Unsupported Media Type, got {r.status_code}"
    assert r.json() == {"detail": "Only text/csv files are accepted"}


def test_exactly_the_limit_is_allowed(client):
    lines, rest = divmod(MAX - 3, 8)
    body = b"id\n" + b"abcdefg\n" * lines + b"x" * rest       # many short rows, exactly MAX bytes
    assert len(body) == MAX
    r = send(client, "edge.csv", body)
    assert r.status_code == 200, f"A file of exactly MAX_BYTES must be accepted (use >, not >=), got {r.status_code}"
    assert r.json()["rows"] == lines + 1, "Every chunk must be kept: rows were lost between chunks."


def test_one_byte_over_is_413(client):
    r = send(client, "big.csv", b"id\n" + b"x" * (MAX - 2))
    assert r.status_code == 413, f"MAX_BYTES + 1 bytes must be refused with 413 Payload Too Large, got {r.status_code}"
    assert r.json() == {"detail": "File larger than 1048576 bytes"}


def test_reads_in_chunks_and_stops_early(client, monkeypatch):
    sizes = []
    original = UploadFile.read

    async def spy(self, size=-1):
        sizes.append(size)
        return await original(self, size)

    monkeypatch.setattr(UploadFile, "read", spy)
    r = send(client, "huge.csv", b"x" * (3 * MAX))
    assert r.status_code == 413
    assert sizes, "The endpoint must read the file with await file.read(CHUNK)."
    assert all(s is not None and 0 < s <= 64 * 1024 for s in sizes), (
        f"file.read was called with sizes {sorted(set(sizes))}: a call without a size (-1) loads the whole upload "
        "into memory. Always read(CHUNK).")
    assert len(sizes) <= MAX // (64 * 1024) + 2, (
        f"{len(sizes)} reads for a 3 MiB file: stop reading as soon as the total passes MAX_BYTES.")


def test_not_utf8_is_400(client):
    r = send(client, "bad.csv", b"\xff\xfe\x00i\x00d\n")
    assert r.status_code == 400, f"Bytes that are not UTF-8 must give 400, got {r.status_code}"
    assert r.json() == {"detail": "File is not UTF-8 text"}


def test_the_type_is_checked_before_reading(client, monkeypatch):
    calls = []
    original = UploadFile.read

    async def spy(self, size=-1):
        calls.append(size)
        return await original(self, size)

    monkeypatch.setattr(UploadFile, "read", spy)
    send(client, "cat.png", b"\x89PNG" + b"x" * 1000, "image/png")
    assert calls == [], "Refuse a wrong content type before reading any of the file."
