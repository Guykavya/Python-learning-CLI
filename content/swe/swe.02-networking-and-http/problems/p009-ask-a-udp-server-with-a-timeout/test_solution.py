import socket
import threading
import time
from contextlib import contextmanager

from solution import udp_ask


@contextmanager
def udp_server(drop_first=0, rogue_first=False, silent=False):
    """A UDP server on a free port. Returns (port, received list). It can drop the first datagrams,
    or first answer from a DIFFERENT port (a stranger), or never answer."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    sock.settimeout(0.05)
    rogue = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rogue.bind(("127.0.0.1", 0))
    seen = []
    stop = threading.Event()

    def loop():
        while not stop.is_set():
            try:
                data, addr = sock.recvfrom(65535)
            except (socket.timeout, OSError):
                continue
            seen.append(data)
            if silent or len(seen) <= drop_first:
                continue
            if rogue_first:
                rogue.sendto(b"FAKE", addr)
            sock.sendto(b"pong:" + data, addr)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    try:
        yield sock.getsockname()[1], seen
    finally:
        stop.set()
        t.join()
        sock.close()
        rogue.close()


def test_simple_answer():
    with udp_server() as (port, seen):
        assert udp_ask(port, "ping", 1.0, 3) == "pong:ping"
        assert seen == [b"ping"], "Exactly one datagram is needed when the first one is answered."


def test_resends_after_a_lost_datagram():
    with udp_server(drop_first=1) as (port, seen):
        assert udp_ask(port, "hi", 0.3, 3) == "pong:hi", "The first datagram was lost: send again after the timeout."
        assert len(seen) == 2


def test_all_lost_gives_none_after_all_tries():
    with udp_server(silent=True) as (port, seen):
        t0 = time.monotonic()
        assert udp_ask(port, "x", 0.15, 3) is None
        elapsed = time.monotonic() - t0
        time.sleep(0.1)
        assert len(seen) == 3, f"tries=3 means three datagrams in all, got {len(seen)}."
        assert 0.4 <= elapsed < 1.5, f"Three waits of 0.15 s each: about 0.45 s in total, took {elapsed:.2f} s."


def test_reply_from_another_port_is_ignored():
    with udp_server(rogue_first=True) as (port, seen):
        assert udp_ask(port, "q", 1.0, 2) == "pong:q", (
            "A datagram from a different port ('FAKE') must be ignored; keep waiting for the real server.")


def test_stray_datagrams_do_not_extend_the_wait():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.settimeout(0.05)
    stop = threading.Event()
    rogue = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def loop():
        while not stop.is_set():
            try:
                _, addr = sock.recvfrom(100)
            except (socket.timeout, OSError):
                continue
            for _ in range(30):                # spam from the wrong port, never the real answer
                rogue.sendto(b"junk", addr)
                time.sleep(0.02)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    try:
        t0 = time.monotonic()
        assert udp_ask(port, "q", 0.3, 1) is None
        assert time.monotonic() - t0 < 0.9, "Junk must not restart the timeout: wait for the REST of the deadline."
    finally:
        stop.set()
        t.join()
        sock.close()
        rogue.close()
