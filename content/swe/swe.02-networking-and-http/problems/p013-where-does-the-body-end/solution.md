## Approach

| # | Rule that ends the body | Body | Reuse |
|---|---|---|---|
| 1 | `Content-Length: 5`: exactly 5 bytes | `Hello` | yes: `WORLD` is the start of the next response on the same connection (a client that keeps it in the body is wrong) |
| 2 | chunked: the chunks `4` + `Wiki`, `5` + `pedia`, then `0` | `Wikipedia` | yes: the message is complete and framed |
| 3 | no length, no chunking: **read until the server closes** | `until the end` | no: the connection is closed by the server; it is the only way the end was marked |
| 4 | status `204`: **never has a body**; headers about length are ignored | empty | yes: nothing was left to read |

Answer:

```text
1: body=Hello reuse=yes
2: body=Wikipedia reuse=yes
3: body=until the end reuse=no
4: body=<empty> reuse=yes
```

## Complexity

Not applicable.

## Another way

Write the four responses into a test for your `decode_chunked` (problem 12) and a small body reader, and run them: the table is the specification.

## Why it matters

Keep-alive depends on every message knowing where it ends. A wrong guess about the end of a body means the next response is read from the middle (a corrupt response, or a hang). Rule order for a client: no-body statuses, chunked, `Content-Length`, close.
