## Approach

A format string is the whole specification of the layout. `<` fixes the byte order (little-endian,
like x86 and ARM computers) and turns off alignment padding, so every field sits at a fixed offset and
the file is the same on every machine. Packing is one `struct.pack` call; unpacking is one
`struct.unpack` on an exact-size slice.

The two traps are handled explicitly:

- `s` codes **truncate** silently, so the name length is checked in bytes (UTF-8 can use 2 to 4 bytes
  per character) before packing.
- A damaged file could have fewer bytes than the header promises. `iter_unpack` would raise a
  `struct.error` for a partial record, but a file with whole records missing would quietly give a
  short list; comparing the body length with `count * 20` catches both.

## Code

```python
import struct

HEADER = "<4sHHIq"
RECORD = "<Id8s"
MAGIC = b"KVLG"
HEADER_SIZE = struct.calcsize(HEADER)   # 20
RECORD_SIZE = struct.calcsize(RECORD)   # 20


def pack_header(version, flags, count, timestamp):
    return struct.pack(HEADER, MAGIC, version, flags, count, timestamp)


def unpack_header(data):
    if len(data) < HEADER_SIZE:
        raise ValueError(f"header needs {HEADER_SIZE} bytes, got {len(data)}")
    magic, version, flags, count, timestamp = struct.unpack(HEADER, data[:HEADER_SIZE])
    if magic != MAGIC:
        raise ValueError(f"bad magic {magic!r}")
    return {"version": version, "flags": flags, "count": count, "timestamp": timestamp}


def pack_record(rec_id, value, name):
    raw = name.encode("utf-8")
    if len(raw) > 8:
        raise ValueError(f"name {name!r} is {len(raw)} bytes; the limit is 8")
    return struct.pack(RECORD, rec_id, value, raw)


def _decode(rec_id, value, raw):
    return (rec_id, value, raw.rstrip(b"\x00").decode("utf-8"))


def unpack_record(data):
    return _decode(*struct.unpack(RECORD, data))


def write_file(path, records, timestamp, version=1, flags=0):
    with open(path, "wb") as f:
        f.write(pack_header(version, flags, len(records), timestamp))
        for rec_id, value, name in records:
            f.write(pack_record(rec_id, value, name))


def read_file(path):
    with open(path, "rb") as f:
        data = f.read()
    header = unpack_header(data)
    body = data[HEADER_SIZE:]
    if len(body) != header["count"] * RECORD_SIZE:
        raise ValueError(f"expected {header['count']} records, file has {len(body)} bytes of records")
    records = [_decode(*fields) for fields in struct.iter_unpack(RECORD, body)]
    return header, records
```

## Complexity

O(n) for n records, both ways; every record is a fixed 20 bytes, so record `i` can also be read
directly at offset `20 + 20 * i` with `f.seek` (random access, the big advantage of fixed-size records).

## Another way

A compiled `struct.Struct(RECORD)` object parses the format once and has `.pack`, `.unpack`,
`.iter_unpack` and `.size`: slightly faster when you pack many records. For single integers,
`int.to_bytes(4, "little")` and `int.from_bytes(data, "little")` do the same job as `"<I"`.
