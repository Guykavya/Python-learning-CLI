def recv_exactly(sock, n):
    # TODO: loop until n bytes arrived; b"" from recv means the peer closed
    return sock.recv(n)
