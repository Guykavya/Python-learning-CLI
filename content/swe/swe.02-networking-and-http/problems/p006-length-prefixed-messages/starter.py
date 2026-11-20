import struct

LIMIT = 1_048_576


def send_message(sock, text):
    # TODO: 4-byte big-endian length of the UTF-8 BYTES, then the bytes
    pass


def recv_message(sock):
    # TODO: header (None on a clean close), size check, body, decode
    return None
