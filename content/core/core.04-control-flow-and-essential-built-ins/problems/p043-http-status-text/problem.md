# HTTP status text with match

Web servers answer with a 3-digit status code. Read a whole-number code and print
`<code> <text>`:

| Code | Text |
|---|---|
| 200 | `OK` |
| 201 | `Created` |
| 204 | `No Content` |
| 301, 302, 307 or 308 | `Redirect` |
| 401 or 403 | `Not Allowed` |
| 404 | `Not Found` |
| any other code from 400 to 499 | `Client Error` |
| any code from 500 to 599 | `Server Error` |
| anything else | `Unknown` |

**Example:** `404` gives `404 Not Found`; `418` gives `418 Client Error`.

**Rule for this problem:** use `match`/`case` with literal patterns, OR patterns (`|`),
guards and the wildcard `_`. The tests check that you use `match`.
