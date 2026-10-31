## Approach

Do the two checks for every call: effective level first, then each handler on the path.

| Call | Effective level | Passes? | Handlers that emit | Lines |
|---|---|---|---|---|
| `app.debug("1")` | INFO | no | | 0 |
| `app.info("2")` | INFO | yes | app (DEBUG); root handler is WARNING, so no | 1 |
| `app.warning("3")` | INFO | yes | app and root | 2 |
| `db.info("4")` | INFO (from `app`) | yes | app's handler; root's no | 1 |
| `db.debug("5")` | INFO | no | | 0 |
| `db.error("6")` | INFO | yes | app and root | 2 |
| `web.debug("7")` | DEBUG | yes | web's handler is ERROR, so no; no propagation | 0 |
| `web.error("8")` | DEBUG | yes | web only (propagate False) | 1 |
| `other.warning("9")` | ERROR (from root) | no | | 0 |
| `other.error("10")` | ERROR | yes | root | 1 |
| `db.critical("11")` | | disabled | | 0 |

Two lessons that explain most "my log line is missing / printed twice" bugs:

- The root logger is set to `ERROR`, yet `app WARNING 3` is printed by the root's handler. A
  propagated record skips the **ancestor loggers'** levels and meets only their **handlers'**
  levels.
- Lines 3 and 6 appear **twice** because the record is emitted by `app`'s handler and again by
  the root's handler. That is the classic duplicate-line bug; `propagate = False` (as on
  `app.web`) is one cure.

`%(name)s` is the name of the logger the call was made on (`app.db`), not of the logger whose
handler printed it.

## Output

```text
app INFO 2
app WARNING 3
app WARNING 3
app.db INFO 4
app.db ERROR 6
app.db ERROR 6
app.web ERROR 8
other ERROR 10
done
```
