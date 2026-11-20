## Hint 1

What do you store per note, besides the text? What turns that into an ETag text, and why should the ETag change after every update? Which status code is for "you did not tell me which version you edited", and which for "you told me, but it is old"?

## Hint 2

Write one small helper `etag_of(version)` and use it in both `GET` and `PUT`. In `PUT`, do the checks in this order: note exists (404), header present (428), header equals the current ETag (412), then write. Why must the last two steps (compare, then write) happen inside one `with lock:`?

## Hint 3

```text
notes = {id: {"note": text, "version": 1}};  lock = Lock()
etag_of(v) = '"' + sha256(str(v)).hexdigest()[:16] + '"'
GET: 404 if missing; set response.headers["ETag"] = etag_of(version); return {...}
PUT: with lock:
        404 if missing; 428 if if_match is None
        if if_match != etag_of(version): 412
        note = text; version += 1
     set the new ETag header; return {...}
```
