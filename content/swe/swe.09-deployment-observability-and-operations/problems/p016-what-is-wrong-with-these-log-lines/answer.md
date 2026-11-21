## Model answer

**(a)** `print` of a password and an e-mail. A password in a log is a leak (logs are copied to backups, dashboards and vendors), and the e-mail is personal data. `print` also bypasses the logger: no level, no request id, not JSON. Instead: `log.info("login ok", extra={"fields": {"user_id": user.id}})`, and never log the password at all.

**(b)** The whole request body of every request. It contains passwords, tokens and personal data, it can be megabytes, and it is expensive. Instead log what you need to debug: method, path, status, duration and, when useful, the size (`"bytes": len(body)`); log bodies only for a sampled, redacted debug mode.

**(c)** The facts are formatted **into the message** with an f-string: `msg` is different for every order, so nobody can count or search "order created" with `jq`, and the e-mail address is personal data. Instead a constant message and fields: `log.info("order created", extra={"fields": {"order_id": order.id, "user_id": user.id, "total_cents": order.total_cents}})`.

**(d)** The traceback is split into **many records**, one per line. They lose their structure (one error becomes 30 events), may interleave with lines of other requests, and only the first few records carry meaning on their own. Instead: `log.exception("unhandled error")` once; the formatter puts the whole traceback in **one** `exception` field of one record with the request id.

**(e)** `print("starting up")`: no level, no timestamp, no request id, not JSON, and (with buffered output) it may appear late. Instead: `log.info("starting", extra={"fields": {"version": settings.version, "env": settings.env}})`, which also records which version is running.

**(f)** A failure logged at `INFO`. Alerts and dashboards filter by level; an operation that failed belongs at `WARNING` (handled, expected: a card decline is the customer's problem) or `ERROR` (our failure). Also the reason belongs in a field. Instead: `log.warning("payment declined", extra={"fields": {"order_id": order.id, "reason": "card_declined"}})`.

**Checklist: your answer should mention**
- [ ] (a) a password and an e-mail in a log: secrets and personal data never go into logs; `print` has no level or request id
- [ ] (b) whole request bodies: sensitive, large, expensive; log method, path, status, duration, size
- [ ] (c) facts formatted into the message with an f-string: use a constant `msg` and extra fields; also personal data
- [ ] (d) a traceback split over several records: use `log.exception` once, one `exception` field
- [ ] (e) `print` instead of a logger: no level, no timestamp, no request id, not JSON
- [ ] (f) a failure logged at INFO: levels have meaning; use WARNING or ERROR, and put the reason in a field
