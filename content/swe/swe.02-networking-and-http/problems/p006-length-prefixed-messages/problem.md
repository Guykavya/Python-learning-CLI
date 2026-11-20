# Length-prefixed messages

Chapter section 6.4: the sender puts the **length of the message** in front, so the reader knows where it ends. Write

```python
send_message(sock, text)      # sends one message
recv_message(sock)            # returns one message as str, or None
```

Format of one message: **4 bytes** with the length of the body, **big-endian** (`struct.pack(">I", n)`), then the body, which is `text` encoded as **UTF-8**.

- The length counts **bytes**, not characters: `"héllo"` is 5 characters but 6 bytes, an emoji is 4 bytes.
- `recv_message` returns the text. If the peer closed the connection **cleanly between two messages** (no byte of a header arrived), it returns `None`.
- If the connection closes **in the middle** of a header or a body, raise `ConnectionError`.
- A length above **1 048 576** bytes (1 MiB) raises `ValueError` **before** reading the body (a hostile peer could claim 4 GB).
- Several messages sent back to back must be read one by one, however the network cuts the bytes.

## Example

```python
import socket
a, b = socket.socketpair()
send_message(a, "hi"); send_message(a, "héllo 😀")
print(recv_message(b))    # hi
print(recv_message(b))    # héllo 😀
a.close()
print(recv_message(b))    # None
```
