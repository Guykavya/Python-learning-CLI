import socket
import struct
import threading
import time

import pytest

from solution import recv_message, send_message


def pair():
    a, b = socket.socketpair()
    a.settimeout(5)
    b.settimeout(5)
    return a, b


def test_three_messages_back_to_back():
    a, b = pair()
    try:
        for t in ("one", "two", "three"):
            send_message(a, t)
        assert [recv_message(b) for _ in range(3)] == ["one", "two", "three"]
    finally:
        a.close()
        b.close()


def test_the_length_counts_bytes_not_characters():
    a, b = pair()
    try:
        send_message(a, "héllo 😀")
        raw = b.recv(100)
        body = "héllo 😀".encode("utf-8")
        assert raw[:4] == struct.pack(">I", len(body)), (
            f"The header must hold the number of BYTES ({len(body)}), big-endian, not the number of characters (7).")
        assert raw[4:] == body
        send_message(a, "héllo 😀")
        assert recv_message(b) == "héllo 😀"
    finally:
        a.close()
        b.close()


def test_empty_message_is_not_the_end():
    a, b = pair()
    try:
        send_message(a, "")
        send_message(a, "x")
        assert recv_message(b) == "", "An empty message is a message (length 0), different from a closed connection."
        assert recv_message(b) == "x"
    finally:
        a.close()
        b.close()


def test_bytes_arriving_in_odd_pieces():
    a, b = pair()
    wire = struct.pack(">I", 11) + b"hello world" + struct.pack(">I", 2) + b"ok"

    def writer():
        for i in range(0, len(wire), 3):          # 3 bytes at a time: the header is cut in the middle
            a.sendall(wire[i:i + 3])
            time.sleep(0.002)

    t = threading.Thread(target=writer, daemon=True)
    t.start()
    try:
        assert recv_message(b) == "hello world"
        assert recv_message(b) == "ok"
    finally:
        t.join()
        a.close()
        b.close()


def test_clean_close_gives_none():
    a, b = pair()
    try:
        send_message(a, "last")
        a.close()
        assert recv_message(b) == "last"
        assert recv_message(b) is None, "A close between two messages is the normal end: return None."
    finally:
        b.close()


def test_close_in_the_middle_is_an_error():
    a, b = pair()
    try:
        a.sendall(struct.pack(">I", 10) + b"abc")
        a.close()
        with pytest.raises(ConnectionError):
            recv_message(b)
    finally:
        b.close()
    a, b = pair()
    try:
        a.sendall(b"\x00\x00")           # half a header
        a.close()
        with pytest.raises(ConnectionError):
            recv_message(b)
    finally:
        b.close()


def test_huge_length_is_refused_before_reading():
    a, b = pair()
    try:
        a.sendall(struct.pack(">I", 4_000_000_000))
        with pytest.raises(ValueError):
            recv_message(b)
    finally:
        a.close()
        b.close()
