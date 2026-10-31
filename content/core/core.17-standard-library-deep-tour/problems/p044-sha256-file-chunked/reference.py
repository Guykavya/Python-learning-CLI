import hashlib


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_stream(f, chunk_size=65536):
    h = hashlib.sha256()
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        h.update(chunk)
    return h.hexdigest()


def sha256_file(path, chunk_size=65536):
    with open(path, "rb") as f:
        return sha256_stream(f, chunk_size)


def matches(path, expected_hex):
    return sha256_file(path) == expected_hex.strip().lower()
