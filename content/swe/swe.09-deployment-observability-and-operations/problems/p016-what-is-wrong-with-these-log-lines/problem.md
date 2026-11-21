# What is wrong with these log lines?

Chapter sections 8.1 (from text to events), 8.2 (the request ID) and 8.6, and "Try it: what is wrong with these log lines?". Six lines of code from one service, each written in a hurry. For **each** one, in `answer.md`, say **what is wrong** (one sentence) and **how you would write it instead** (one line of code or one sentence).

```python
# (a) in the login view
print(f"login ok for {user.email} with password {password}")

# (b) in a middleware
log.info("incoming request: %s", request.body)                  # the whole body of every request

# (c) after an order is saved
log.info(f"order {order.id} created by {user.email} for {order.total_cents} cents")

# (d) in an error handler
for text in traceback.format_exc().splitlines():
    log.error(text)                                             # one log record per line of the traceback

# (e) at start-up
print("starting up")

# (f) when the card is declined
log.info("payment failed: card declined for order %s", order.id)
```

Use the rules of chapter 8.1: one event per line as JSON on stdout, fixed field names, extra fields for the facts, levels with meaning, no secrets and no personal data, no health probes.

Write about 200 to 350 words in total.

## Example

For a line like `log.debug(f"x={x}")` in a loop of 2 million rows: "wrong: one record per row hides the real events and costs money; instead log a summary every N rows or at the end, with counts and duration."
