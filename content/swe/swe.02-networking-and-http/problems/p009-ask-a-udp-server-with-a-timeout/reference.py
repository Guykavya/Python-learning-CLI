import socket
import time


def udp_ask(port, text, timeout, tries):
    server = ("127.0.0.1", port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        for _ in range(tries):
            sock.sendto(text.encode("utf-8"), server)
            deadline = time.monotonic() + timeout
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                sock.settimeout(remaining)
                try:
                    data, addr = sock.recvfrom(65535)
                except socket.timeout:
                    break
                if addr == server:
                    return data.decode("utf-8")
        return None
    finally:
        sock.close()
