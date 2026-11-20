import socket

from solution import start_echo_server


def connect(port):
    s = socket.create_connection(("127.0.0.1", port), timeout=5)
    s.settimeout(5)
    return s


def test_upper_cases_the_message():
    server, port = start_echo_server()
    try:
        assert port > 0 and port == server.getsockname()[1], (
            "Return the real port: bind to port 0 and read it back with getsockname()[1].")
        with connect(port) as c:
            c.sendall(b"hello")
            assert c.recv(100) == b"HELLO"
            c.sendall(b"again")
            assert c.recv(100) == b"AGAIN", "The same connection must keep working for more messages."
    finally:
        server.close()


def test_two_clients_at_the_same_time():
    server, port = start_echo_server()
    try:
        a, b = connect(port), connect(port)
        try:
            a.sendall(b"first")
            assert a.recv(100) == b"FIRST"
            b.sendall(b"second")
            assert b.recv(100) == b"SECOND", (
                "The second client got no answer while the first is still connected: serve each client in its own thread.")
            a.sendall(b"more")
            assert a.recv(100) == b"MORE"
        finally:
            a.close()
            b.close()
    finally:
        server.close()


def test_ports_are_not_hard_coded():
    s1, p1 = start_echo_server()
    s2, p2 = start_echo_server()
    try:
        assert p1 != p2, "Two servers must get two different ports: use port 0 and getsockname()."
    finally:
        s1.close()
        s2.close()


def test_binds_to_loopback_only():
    server, port = start_echo_server()
    try:
        assert server.getsockname()[0] == "127.0.0.1", "Bind to 127.0.0.1, not 0.0.0.0: tests must not open the machine to the network."
    finally:
        server.close()


def test_closing_the_server_socket_stops_accepting():
    server, port = start_echo_server()
    server.close()
    import time
    time.sleep(0.5)
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=1)
        s.close()
        refused = False
    except OSError:
        refused = True
    assert refused, "After server.close() the port must refuse new connections."
