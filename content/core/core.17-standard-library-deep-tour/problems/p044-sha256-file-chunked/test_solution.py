import hashlib
import io

import pytest

from solution import matches, sha256_file, sha256_stream, sha256_text

ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class SpyReader(io.BytesIO):
    """A binary stream that records the size asked for in every read() call."""

    def __init__(self, data):
        super().__init__(data)
        self.sizes = []

    def read(self, size=-1):
        self.sizes.append(size)
        return super().read(size)


def test_sha256_text_known_values():
    assert sha256_text("abc") == ABC, "sha256 of 'abc' is a published test value: encode the text to UTF-8 bytes and use hexdigest()."
    assert sha256_text("") == EMPTY, "The empty text has a digest too."


def test_sha256_text_utf8():
    expected = hashlib.sha256("café".encode("utf-8")).hexdigest()
    assert sha256_text("café") == expected, "Encode with UTF-8 explicitly; other encodings give other bytes and another digest."
    assert len(sha256_text("x")) == 64 and sha256_text("x") == sha256_text("x").lower(), "hexdigest() gives 64 lowercase hex characters."


def test_stream_reads_in_chunks():
    data = bytes(range(256)) * 40          # 10240 bytes
    spy = SpyReader(data)
    digest = sha256_stream(spy, chunk_size=1000)
    assert digest == hashlib.sha256(data).hexdigest(), "Feeding chunks with update() must give the same digest as hashing all at once."
    assert spy.sizes, "sha256_stream must call f.read(...)."
    assert all(size == 1000 for size in spy.sizes), (
        f"Every read must ask for chunk_size bytes; you called read with {sorted(set(spy.sizes))}. "
        "read() with no argument loads the whole file into memory."
    )
    assert len(spy.sizes) == 12, "10240 bytes in chunks of 1000: 11 reads with data plus one that returns b'' and ends the loop."


def test_stream_empty_and_exact_multiple():
    assert sha256_stream(io.BytesIO(b""), 4) == EMPTY, "An empty stream: the first read returns b'' and the loop must stop at once."
    assert sha256_stream(io.BytesIO(b"abcdefgh"), 4) == hashlib.sha256(b"abcdefgh").hexdigest(), (
        "When the size is an exact multiple of chunk_size, stop on the empty read, not on a short one."
    )


def test_sha256_file(tmp_path):
    path = tmp_path / "abc.bin"
    path.write_bytes(b"abc")
    assert sha256_file(path) == ABC, "Open the file in binary mode ('rb') and hash its bytes."
    assert sha256_file(str(path), chunk_size=1) == ABC, "The chunk size must not change the digest; a str path works too."


def test_sha256_file_binary_exact(tmp_path):
    data = b"line1\r\nline2\n\x00\xff"
    path = tmp_path / "raw.bin"
    path.write_bytes(data)
    assert sha256_file(path, chunk_size=3) == hashlib.sha256(data).hexdigest(), (
        "The bytes must be hashed exactly: text mode would change \\r\\n line endings and fail on \\xff."
    )


def test_sha256_file_large(tmp_path):
    data = b"0123456789" * 100_000      # 1 MB
    path = tmp_path / "big.bin"
    path.write_bytes(data)
    assert sha256_file(path) == hashlib.sha256(data).hexdigest(), "A file bigger than one chunk must be hashed completely."


def test_matches(tmp_path):
    path = tmp_path / "abc.bin"
    path.write_bytes(b"abc")
    assert matches(path, ABC) is True, "Same digest: True."
    assert matches(path, "  " + ABC.upper() + "\n") is True, "Strip spaces and compare lower case: people paste digests in upper case."
    assert matches(path, EMPTY) is False, "A different digest: False."
