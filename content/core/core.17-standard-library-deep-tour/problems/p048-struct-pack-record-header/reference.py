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
