import builtins
import hashlib

from solution import file_sha256


class Spy:
    """Wraps a real file and records the size asked in every read call."""

    sizes = []

    def __init__(self, real):
        self._real = real

    def __enter__(self):
        self._real.__enter__()
        return self

    def __exit__(self, *exc):
        return self._real.__exit__(*exc)

    def read(self, *args):
        Spy.sizes.append(args[0] if args else None)
        return self._real.read(*args)

    def __getattr__(self, name):
        return getattr(self._real, name)


def write(tmp_path, data, name="f.bin"):
    path = tmp_path / name
    path.write_bytes(data)
    return path


def test_abc(tmp_path):
    path = write(tmp_path, b"abc")
    assert file_sha256(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", "Wrong hash. Return h.hexdigest() of sha256, with the bytes of the file."


def test_empty_file(tmp_path):
    path = write(tmp_path, b"")
    assert file_sha256(path) == hashlib.sha256(b"").hexdigest(), "An empty file still has a hash. The loop must simply not run."


def test_big_file_same_as_whole(tmp_path):
    data = bytes(range(256)) * 1200
    path = write(tmp_path, data)
    assert file_sha256(path) == hashlib.sha256(data).hexdigest(), "Chunks must give the same hash as the whole file. Use one hash object and call update for every chunk."


def test_tiny_chunks(tmp_path):
    data = b"The quick brown fox jumps over the lazy dog" * 3
    path = write(tmp_path, data)
    assert file_sha256(path, chunk_size=1) == hashlib.sha256(data).hexdigest(), "chunk_size=1 reads one byte at a time. The result must still be the same."
    assert file_sha256(path, chunk_size=7) == hashlib.sha256(data).hexdigest(), "The last chunk is shorter than chunk_size. Do not drop it."


def test_exact_multiple_of_chunk(tmp_path):
    data = b"x" * 100
    path = write(tmp_path, data)
    assert file_sha256(path, chunk_size=10) == hashlib.sha256(data).hexdigest(), "When the size is an exact multiple of the chunk, the next read returns b'' and must stop the loop."


def test_never_reads_more_than_chunk(tmp_path, monkeypatch):
    data = b"a" * 5000
    path = write(tmp_path, data)
    real_open = builtins.open
    Spy.sizes = []
    monkeypatch.setattr(builtins, "open", lambda *a, **k: Spy(real_open(*a, **k)))
    assert file_sha256(path, chunk_size=1000) == hashlib.sha256(data).hexdigest(), "Wrong hash."
    assert Spy.sizes, "Open the file with open(path, 'rb') and call f.read(chunk_size)."
    assert None not in Spy.sizes, "f.read() without a size reads the whole file. Pass chunk_size."
    assert max(Spy.sizes) <= 1000, "Never ask for more than chunk_size bytes in one read."
