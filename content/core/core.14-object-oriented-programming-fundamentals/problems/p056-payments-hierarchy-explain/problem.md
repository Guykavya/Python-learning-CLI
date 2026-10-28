# Explain: design the exception hierarchy of a payments library

You are writing `paykit`, a small library that shops use to charge cards through a payment gateway.
Today every problem is raised as `Exception("...")` with a different text, and shop developers write
code like this:

```python
try:
    paykit.charge(card, 49900)
except Exception as e:
    if "declined" in str(e):
        show("Your card was declined")
    elif "timeout" in str(e) or "503" in str(e):
        retry_later()
    else:
        raise
```

These are the problems `paykit` must report:

- the card number fails the checksum; the expiry date is in the past; the amount is zero or negative;
- the bank declines the card (with a decline code such as `"insufficient_funds"` or `"stolen_card"`);
- the same order id is charged twice;
- a refund is larger than the original charge;
- the network times out, or the gateway answers HTTP 503 (both are worth retrying later);
- the gateway answers with something `paykit` cannot understand (a bug or an API change);
- the shop forgot to configure the API key.

In `answer.md` (about 300 to 450 words, plus a class sketch), explain:

1. **The base class.** Why should `paykit` have one base exception, and what is its name? What does it
   let a caller do that `except Exception` cannot?
2. **The groups.** Sketch the hierarchy (class names and parents, as Python `class` lines or an
   indented tree). Group the errors by **what the caller should do** about them, not by where they
   happen in the code. Which group is "retry later", which is "tell the customer", which is "the
   developer must fix something"?
3. **Extra attributes.** Which exceptions should carry data, and which data (for example the decline
   code, the amount, a `retry_after` value)? Why is an attribute better than parsing `str(e)`?
4. **Chaining.** When `paykit` catches a low-level error (`TimeoutError`, `json.JSONDecodeError`), how
   should it re-raise its own exception, and why? When would `from None` be acceptable?
5. **The caller's code.** Rewrite the `try` block above with your hierarchy. In what order must the
   `except` clauses be, and why?
6. **One trap.** Should an invalid amount also be a `ValueError`? Give your choice and the reason.

## Example of the level of detail

"`class CardDeclined(PaymentError)` carries `self.decline_code`, so the shop can show a different
message for `"stolen_card"` without searching the message text, which may change in the next version."
A good answer goes on like this for each point.
