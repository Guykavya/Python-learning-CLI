## Hint 1

Ask the same question for each response: *which rule says where this body ends?* The rules, in the order a client checks them: no body by status (204, 304, 1xx, HEAD), then `Transfer-Encoding: chunked`, then `Content-Length`, then "until the server closes".

## Hint 2

Response 1: `Content-Length: 5` means exactly five bytes: `Hello`. Everything after belongs to the **next** response on the connection. Response 2: join the chunk data, `Wiki` + `pedia`.

## Hint 3

A body that ends only when the server closes the connection leaves nothing to reuse (`reuse=no`). A `204` has no body by definition: the length header is ignored (and it should not be there), and the connection stays usable.
