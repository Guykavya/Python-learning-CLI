import socket
import threading
import time

import pytest

from solution import recv_exactly


def pair():
    a, b = socket.socketpair()
    a.settimeout(5)
    b.settimeout(5)
    return a, b


def test_bytes_that_arrive_one_at_a_time():
    a, b = pair()

    def writer():
        for byte in b"abcdefghij":
            a.sendall(bytes([byte]))
            time.sleep(0.002)

    t = threading.Thread(target=writer, daemon=True)
    t.start()
    try:
        assert recv_exactly(b, 10) == b"abcdefghij", "recv returns whatever has arrived: loop until all 10 bytes are there."
    finally:
        t.join()
        a.close()
        b.close()


def test_does_not_read_more_than_n():
    a, b = pair()
    try:
        a.sendall(b"hello world")
        assert recv_exactly(b, 5) == b"hello"
        assert recv_exactly(b, 6) == b" world", "The rest of the stream must stay in the socket for the next call."
    finally:
        a.close()
        b.close()


def test_zero_bytes():
    a, b = pair()
    try:
        b.settimeout(0.2)
        assert recv_exactly(b, 0) == b"", "n = 0 returns b'' at once, without waiting for data."
    finally:
        a.close()
        b.close()


def test_closed_early_says_how_many_arrived():
    a, b = pair()
    try:
        a.sendall(b"abc")
        a.close()
        with pytest.raises(ConnectionError) as e:
            recv_exactly(b, 10)
        msg = str(e.value)
        assert "3" in msg and "10" in msg, f"The message must say how many bytes arrived (3) and were expected (10). Got: {msg!r}"
    finally:
        b.close()


def test_closed_before_anything():
    a, b = pair()
    try:
        a.close()
        with pytest.raises(ConnectionError):
            recv_exactly(b, 4)
    finally:
        b.close()


def test_big_message_in_pieces():
    a, b = pair()
    data = bytes(range(256)) * 400          # 102400 bytes
    t = threading.Thread(target=lambda: a.sendall(data), daemon=True)
    t.start()
    try:
        assert recv_exactly(b, len(data)) == data
    finally:
        t.join()
        a.close()
        b.close()
