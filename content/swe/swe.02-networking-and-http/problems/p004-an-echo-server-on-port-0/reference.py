import socket
import threading


def _serve_client(conn):
    with conn:
        while True:
            try:
                data = conn.recv(4096)
            except OSError:
                return
            if not data:
                return
            conn.sendall(data.upper())


def _accept_loop(server):
    while True:
        try:
            conn, _ = server.accept()
        except socket.timeout:          # wake up regularly: a closed server socket is noticed here
            continue
        except OSError:                 # the listening socket was closed
            return
        conn.settimeout(None)
        threading.Thread(target=_serve_client, args=(conn,), daemon=True).start()


def start_echo_server():
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen()
    server.settimeout(0.1)
    port = server.getsockname()[1]
    threading.Thread(target=_accept_loop, args=(server,), daemon=True).start()
    return server, port
