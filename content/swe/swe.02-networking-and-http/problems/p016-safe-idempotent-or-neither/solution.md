## Approach

Update the three values after every call:

| Call | Effect | Status | orders | a1 | counter |
|---|---|---|---|---|---|
| 1 `GET /a/1` | none (no key yet) | 404 | 0 | - | 0 |
| 2 `POST /orders` | append | 201 | 1 | - | 0 |
| 3 `POST /orders` | append again | 201 | 2 | - | 0 |
| 4 `PUT /a/1` | create key | 201 | 2 | 7 | 0 |
| 5 `PUT /a/1` | same value again | 200 | 2 | 7 | 0 |
| 6 `PATCH /counter` | add 1 | 200 | 2 | 7 | 1 |
| 7 `PATCH /counter` | add 1 again | 200 | 2 | 7 | 2 |
| 8 `DELETE /a/1` | remove | 204 | 2 | - | 2 |
| 9 `DELETE /a/1` | nothing to remove | 404 | 2 | - | 2 |
| 10 `GET /orders` | none | 200 | 2 | - | 2 |

(The ten lines were also produced by running a simulation of these rules.)

- **Safe** (never changes state): `GET`.
- **Idempotent** (repeating changes nothing more): `PUT` (calls 4 and 5), `DELETE` (8 and 9), and `GET`.
- **Neither**: `POST /orders` created a second order, and this `PATCH` (an increment) added twice.

"Idempotent" is about the **state of the server** after repeating, not about the status code: the second `PUT` says `200` instead of `201` and the second `DELETE` says `404` instead of `204`, but the data is the same. `PATCH` is idempotent only if it says "set to 5", not "add 1".

## Complexity

Not applicable.

## Another way

Draw the state as a small table with a column for each of the three things and write one row per call. A repeated call that leaves the row unchanged is idempotent.

## Why it matters

This is why retry rules treat `POST` differently from `PUT` (chapter section 9.2): repeating the call changes the data only for `POST`, for an incrementing `PATCH`, and not for `PUT` or `DELETE`.
