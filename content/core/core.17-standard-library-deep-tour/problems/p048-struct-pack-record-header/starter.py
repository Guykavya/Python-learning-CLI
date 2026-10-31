import struct

HEADER = "<4sHHIq"
RECORD = "<Id8s"
MAGIC = b"KVLG"


def pack_header(version, flags, count, timestamp):
    return b""


def unpack_header(data):
    return {}


def pack_record(rec_id, value, name):
    return b""


def unpack_record(data):
    return (0, 0.0, "")


def write_file(path, records, timestamp, version=1, flags=0):
    pass


def read_file(path):
    return {}, []
