# Fix the IDOR

Chapter sections 8.1 to 8.3 and "Try it: fix this". `starter.py` is a small notes API (FastAPI and SQLite). Three endpoints load a note **by its id only**:

- `GET /notes/{id}` reads it,
- `PATCH /notes/{id}` changes its text,
- `DELETE /notes/{id}` deletes it,

without asking whose note it is. So Ravi can read, change and delete Asha's notes by guessing a number. This is an **IDOR** (insecure direct object reference). Random-looking ids would not fix it (chapter 8.2); the check is what fixes it.

Copy `starter.py` to `solution.py` and fix the three endpoints:

1. Scope every query by the caller: add `AND owner_id = ?` with the logged-in user's id, in the `SELECT`, the `UPDATE` and the `DELETE` (section 8.3, the first and best fix: no gap between "fetch" and "check").
2. When no row matches, answer **404 `note not found`**. "Not yours" must look exactly like "does not exist": same status, same body.

Do not change anything else. Creating a note, listing your own notes and the 401 for a missing token already work. Tokens: `t-asha` is user 1 and `t-ravi` is user 2 (`Authorization: Bearer t-asha`). The tests use both users and also check that Asha's note is **unchanged** after Ravi's attempt: a bug that answers 404 *after* doing the update would fail.

## Example

```text
Asha:  POST /notes {"text": "plan"}        -> 201 {"id": 1, "text": "plan"}
Ravi:  GET /notes/1                        -> 404 {"detail": "note not found"}    (was 200)
Ravi:  DELETE /notes/1                     -> 404                                  (was 200, and the note was gone)
Asha:  GET /notes/1                        -> 200 {"id": 1, "text": "plan"}
```
