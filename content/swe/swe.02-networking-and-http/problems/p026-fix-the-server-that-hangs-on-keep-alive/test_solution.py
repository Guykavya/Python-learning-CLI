import socket
import threading

import pytest

from solution import serve_connection


def request(body):
    return b"POST /x HTTP/1.1\r\nHost: t\r\nContent-Length: %d\r\n\r\n" % len(body) + body


def read_response(sock):
    data = b""
    try:
        while b"\r\n\r\n" not in data:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        head, _, rest = data.partition(b"\r\n\r\n")
        length = int(head.lower().split(b"content-length:")[1].split(b"\r\n")[0])
        while len(rest) < length:
            rest += sock.recv(4096)
    except socket.timeout:
        pytest.fail("No answer within 2 seconds: the server waited for EOF (it reads the body until the client closes the "
                    "connection). Read exactly Content-Length bytes.")
    return head.split(b"\r\n")[0], rest[:length], rest[length:]


@pytest.fixture
def pair():
    server_side, client = socket.socketpair()
    client.settimeout(2)
    t = threading.Thread(target=serve_connection, args=(server_side,), daemon=True)
    t.start()
    yield client, t
    client.close()
    server_side.close()
    t.join(timeout=2)


def test_two_requests_on_one_connection(pair):
    client, t = pair
    client.sendall(request(b"hello"))
    status, body, extra = read_response(client)
    assert status == b"HTTP/1.1 200 OK" and body == b"5" and extra == b""
    client.sendall(request(b"abc"))
    status, body, extra = read_response(client)
    assert body == b"3", "The second request on the same connection must be answered too."


def test_pipelined_requests_in_one_send(pair):
    client, t = pair
    client.sendall(request(b"aa") + request(b"bbbb"))
    s1, b1, rest = read_response(client)
    assert b1 == b"2"
    if rest:                                         # the second answer may already be in the buffer
        assert rest.endswith(b"4")
    else:
        s2, b2, _ = read_response(client)
        assert b2 == b"4", "Bytes after the first body belong to the next request: keep them in the buffer."


def test_request_without_a_body(pair):
    client, t = pair
    client.sendall(b"GET / HTTP/1.1\r\nHost: t\r\n\r\n")
    status, body, extra = read_response(client)
    assert body == b"0", "No Content-Length: the body is empty."


def test_body_arriving_in_pieces(pair):
    client, t = pair
    wire = request(b"x" * 10000)
    for i in range(0, len(wire), 1000):
        client.sendall(wire[i:i + 1000])
    status, body, extra = read_response(client)
    assert body == b"10000"


def test_the_function_returns_when_the_client_closes(pair):
    client, t = pair
    client.sendall(request(b"hi"))
    read_response(client)
    client.close()
    t.join(timeout=2)
    assert not t.is_alive(), "serve_connection must return when the client closes the connection."


def test_client_leaves_in_the_middle_of_a_body():
    server_side, client = socket.socketpair()
    t = threading.Thread(target=serve_connection, args=(server_side,), daemon=True)
    t.start()
    client.sendall(b"POST / HTTP/1.1\r\nHost: t\r\nContent-Length: 100\r\n\r\nonly a few")
    client.close()
    t.join(timeout=2)
    server_side.close()
    assert not t.is_alive(), "A client that leaves in the middle of a body must not keep the server waiting."
