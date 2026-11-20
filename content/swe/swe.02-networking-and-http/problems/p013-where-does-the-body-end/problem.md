# Where does the body end?

A client reads four responses from servers. For each, work out **the exact body** the client must hand to its caller, and whether the **connection can be reused** for another request afterwards (chapter section 8.4 and 15.4). Line ends are `\r\n`. Nothing else arrives on these connections except the bytes shown.

```text
Response 1
HTTP/1.1 200 OK
Content-Length: 5

HelloWORLD

Response 2
HTTP/1.1 200 OK
Transfer-Encoding: chunked

4
Wiki
5
pedia
0
(empty line)

Response 3
HTTP/1.1 200 OK
Connection: close

until the end (then the server closes the connection)

Response 4
HTTP/1.1 204 No Content
Content-Length: 4
(empty line, and no more bytes after it; the server keeps the connection open)
```

(In response 1 the text `HelloWORLD` is what the server sent after the blank line. In response 2 every line is followed by `\r\n`, with the chunk sizes in hexadecimal.)

Write your answer in `answer.txt`, one line per response, in exactly this form:

```text
1: body=<the body text> reuse=<yes or no>
```

Write `<empty>` for an empty body. Do not run anything.

## After you answer

1. In response 1, what is `WORLD`? What happens if the client hands it to its caller as part of the body?
2. In response 3, how does the client know the body has ended, and why can the connection not be reused?
3. Why must the client ignore the `Content-Length: 4` of response 4?
