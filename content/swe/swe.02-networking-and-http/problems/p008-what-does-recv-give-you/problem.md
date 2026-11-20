# What does `recv` give you?

A sender writes three messages, each with **one length byte** in front:

```text
sendall(b"\x05HELLO")
sendall(b"\x07WORLD!!")
sendall(b"\x03BYE")
```

TCP is a stream: the receiver is told the bytes arrive in these four pieces (the network cut them differently from the three `sendall` calls). Here the pieces are a list, so that you can follow the code without sockets:

```python
chunks = [b"\x05HEL", b"LO\x07WORLD!", b"!\x03BY", b"E"]

# A. the naive receiver: "one recv = one message"
for c in chunks:
    print("naive:", c)

# B. the framed receiver
buf = b""
for c in chunks:
    buf += c
    while buf:
        n = buf[0]
        if len(buf) < 1 + n:
            break
        print("framed:", buf[1:1 + n])
        buf = buf[1 + n:]
print("left over:", buf)
```

Predict **exactly** what the program prints. `print` shows a bytes value as `b'...'`, with non-printable bytes written as `\x05`, `\x07`, `\x03`.

Write your answer in `answer.txt`, one printed line per line. Do not run it.

## After you answer

1. Which of the three naive lines is a whole message? What are the other three?
2. In the framed loop, what does the `break` do, and when does the loop go on?
3. Why is `"left over:"` empty at the end? What would a non-empty value mean?
