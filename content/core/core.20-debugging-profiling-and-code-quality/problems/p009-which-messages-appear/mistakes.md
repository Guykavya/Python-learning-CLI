- Checking the root logger's level (`ERROR`) for records that propagate into it. Only the root's
  **handler** level (`WARNING`) matters for them.
- Thinking `app.db` has level `NOTSET` = 0 and therefore lets `DEBUG` through. `NOTSET` means
  "ask my parent", and `app` says `INFO`.
- Printing each message once. A record goes through every handler on the way up, so it can be
  printed several times.
- Expecting `web.debug("7")` to appear because `web`'s level is `DEBUG`. Its only handler is set
  to `ERROR`, and it does not propagate.
- Printing `app` as the name for messages from `app.db` because `app`'s handler printed them.
  The record keeps the name of the logger it was created on.
- Expecting `other.warning("9")` to reach the root handler. `other` has no level, so it uses the
  root's `ERROR`, and the record is dropped before any handler.
