# Stop lost updates with ETags

Chapter section 12.6 ("Lost updates: ETag and `If-Match`"). Two staff members open the same note and both save: the second save silently erases the first. This is a **lost update**. The cure is **optimistic concurrency**: every read returns a version label (`ETag`); every write must say which version it was based on (`If-Match`); if the note has changed meanwhile, the server refuses.

Write `build_app(seed)` in `solution.py`. It returns a FastAPI app that keeps notes in memory. `seed` is a dict such as `{1: "original"}` (note id to text). Every note starts at version 1.

**`GET /notes/{note_id}`**

- `200` with JSON `{"id": 1, "note": "original"}` and an `ETag` header.
- `404` if the note does not exist.

**`PUT /notes/{note_id}`** with JSON `{"note": "new text"}` and the header `If-Match`

- note does not exist: `404`;
- no `If-Match` header: **`428`** (Precondition Required);
- `If-Match` is not the **current** ETag (an old one, or any other text): **`412`** (Precondition Failed), and the note is **not** changed;
- `If-Match` is the current ETag: store the text, raise the version by one, answer `200` with `{"id": 1, "note": "new text"}` and the **new** `ETag` header.

**The ETag value.** It is the quoted hash of the version, for example `"3f9c2a..."` (the value including the two double quote characters; for the hash use `hashlib.sha256` of the version text and the first 16 hex digits). It must be the same on every read while the note does not change, and different after every update. The tests treat it as an opaque text: they only check that it starts and ends with `"`, that it is stable, and that it changes.

The "check the version and write" step must be **one step** with nothing in between (use a `threading.Lock` around it): reading the version in one statement and writing in another leaves a gap for a second request (chapter, "Try it: why not read, then write?").

## Example

```text
GET  /notes/1                              -> 200 {"id": 1, "note": "original"}   ETag: "A"
PUT  /notes/1 {"note": "alice"} If-Match "A"   -> 200  ETag: "B"
PUT  /notes/1 {"note": "bob"}   If-Match "A"   -> 412  (bob read version A before alice saved)
PUT  /notes/1 {"note": "x"}     (no header)    -> 428
GET  /notes/1                              -> {"note": "alice"}  ETag: "B"   (bob's text was not stored)
```

The tests import `build_app`.
