## Approach

Real output (course environment, FastAPI 0.162, Python 3.14):

```text
1: 201 /items/pen
2: 202
3: 422
4: 409
5: 410
6: 412
7: 200
8: 200
9: 429 30
10: 500
```

- **1: `201 /items/pen`.** `POST` made something; the decorator sets 201 and the function adds a `Location` header with the new resource's address.
- **2: `202`.** The work is only queued; the answer says "accepted", not "done".
- **3: `422`.** The body is well-formed JSON but `"cheap"` is not an integer. Pydantic rejects it before the function starts (so `ink` is never created).
- **4: `409`.** The data is valid, but it clashes with the current state: `pen` exists (request 1 changed the state).
- **5: `410`.** The resource used to exist and has been removed on purpose; `404` would say "never heard of it".
- **6: `412`.** The client says "only if the version is `v1`"; the current one is `v2`. A precondition failed (chapter section 12.6).
- **7, 8: `200`.** The login counter is 1 and 2: not above 2.
- **9: `429 30`.** The third call exceeds the limit; `Retry-After` tells the client to wait 30 seconds.
- **10: `500`.** `1 / 0` raises `ZeroDivisionError`, which no handler catches: a server error. The client must see a 5xx, because the fault is not theirs.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Sort the codes into families to remember them: 2xx worked, 4xx "you must change the request" (or wait), 5xx "we failed, try again later". Then ask for each request who is responsible for the problem.
