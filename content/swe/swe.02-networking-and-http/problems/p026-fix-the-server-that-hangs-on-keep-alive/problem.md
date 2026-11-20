# Fix the server that hangs on keep-alive

`starter.py` contains `serve_connection(conn)`, the heart of a tiny HTTP server (chapter sections 15.1 and 15.4): it reads requests from **one connection** until the client closes it, and answers each one with `200` and a body that tells how many body bytes it received.

It works with a client that opens a new connection for every request and closes it after sending. But a **keep-alive** client sends a request, waits for the answer, then sends the next request **on the same connection**. With such a client the server never answers: it hangs.

Fix `solution.py` (start from `starter.py`) so that:

1. it reads **exactly `Content-Length` bytes** of body (0 when the header is missing), not "until the client closes";
2. bytes that arrived **after** the body (the next request, if the client sent two at once) are kept for the next round;
3. if the client closes the connection in the middle of a head or a body, the function simply returns;
4. the answer stays exactly `HTTP/1.1 200 OK\r\nContent-Length: <n>\r\n\r\n<digits>`, where the body `<digits>` is the number of body bytes of that request.

You do not need to change anything else.

## What the tests do

They run `serve_connection` on one end of a `socket.socketpair()` in a thread, send two requests **on the same connection** (waiting for each answer, with a 2-second timeout), then two requests sent **in one `sendall`**, then close. A client that waits more than 2 seconds for an answer fails with the message "the server waited for EOF".
