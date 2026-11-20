import re

_HEX = re.compile(rb"[0-9a-fA-F]+")


def decode_chunked(data):
    pos = 0
    body = []
    while True:
        end = data.find(b"\r\n", pos)
        if end == -1:
            raise ValueError("missing chunk size line")
        size_text = data[pos:end].split(b";", 1)[0].strip()
        if not _HEX.fullmatch(size_text):
            raise ValueError(f"chunk size is not hexadecimal: {size_text!r}")
        size = int(size_text, 16)
        pos = end + 2
        if size == 0:
            break
        chunk = data[pos:pos + size]
        if len(chunk) < size:
            raise ValueError("chunk cut short")
        pos += size
        if data[pos:pos + 2] != b"\r\n":
            raise ValueError("missing CRLF after chunk data")
        pos += 2
        body.append(chunk)
    trailers = {}
    while True:
        end = data.find(b"\r\n", pos)
        if end == -1:
            raise ValueError("unterminated trailers")
        line = data[pos:end]
        pos = end + 2
        if line == b"":
            break
        name, colon, value = line.decode("latin-1").partition(":")
        if not colon:
            raise ValueError("malformed trailer line")
        trailers[name.strip().lower()] = value.strip()
    return b"".join(body), trailers
