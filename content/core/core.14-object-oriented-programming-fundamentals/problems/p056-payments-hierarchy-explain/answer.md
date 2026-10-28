**1. One base class.** Every exception that `paykit` raises on purpose inherits from
`class PaykitError(Exception)`. A caller can then write `except PaykitError` to mean "anything that went
wrong inside paykit", while real bugs in their own code (`NameError`, `KeyError`) still crash loudly.
`except Exception` catches both and hides bugs. The base class also documents the library: "these are
the errors I promise to raise".

**2. Groups by what the caller does.**

```python
class PaykitError(Exception): ...                    # base for everything

class ConfigurationError(PaykitError): ...           # developer must fix setup (missing API key)

class InvalidRequest(PaykitError): ...               # caller sent bad data: fix input, do not retry
class InvalidCard(InvalidRequest): ...               # checksum or expiry
class InvalidAmount(InvalidRequest, ValueError): ... # zero/negative, refund > charge
class DuplicateCharge(InvalidRequest): ...           # order id already charged

class CardDeclined(PaykitError): ...                 # tell the customer, ask for another card

class GatewayError(PaykitError): ...                 # problem on the other side
class TemporaryGatewayError(GatewayError): ...       # timeout, HTTP 503: retry later
class UnexpectedResponse(GatewayError): ...          # unknown answer: log it, alert developers
```

"Retry later" is `TemporaryGatewayError`, "tell the customer" is `CardDeclined` (and `InvalidCard`),
"developer must fix" is `ConfigurationError` and `UnexpectedResponse`. The tree follows decisions, so
each `except` clause matches one decision.

**3. Attributes.** `CardDeclined` has `decline_code`; `InvalidAmount` has `amount` (and `limit` for
refunds); `DuplicateCharge` has `order_id`; `TemporaryGatewayError` has `retry_after` (seconds, or
`None`); `UnexpectedResponse` keeps `status` and the raw `body`. Each `__init__` stores the values and
calls `super().__init__(message)` with a readable message. Code reads `e.decline_code`, a stable
interface; message text is for humans and may be reworded or translated in any version.

**4. Chaining.** Inside `paykit`:

```python
try:
    reply = self._send(request)
except TimeoutError as e:
    raise TemporaryGatewayError("gateway timed out", retry_after=30) from e
```

`from e` sets `__cause__`, so the traceback shows both: "the gateway timed out" *and* the original
socket error that explains why. The caller only needs to know paykit's type. `from None` hides the
original; it is acceptable only when the low-level error adds nothing, for example a `KeyError` from a
lookup table that you turn into `InvalidCard("unknown card brand")`.

**5. The caller's code.**

```python
try:
    paykit.charge(card, 49900, order_id="A17")
except CardDeclined as e:
    show(decline_text(e.decline_code))
except TemporaryGatewayError as e:
    retry_later(e.retry_after)
except InvalidRequest as e:
    show_form_error(str(e))
except PaykitError:
    log.exception("payment failed")
    raise
```

Specific classes come first: Python uses the **first** matching `except`, and `except PaykitError` at
the top would swallow all the others.

**6. The trap.** `InvalidAmount(InvalidRequest, ValueError)` is a reasonable choice: an invalid amount
really *is* a wrong value, and code that already handles `ValueError` keeps working. But it must stay a
`PaykitError` too, so `except PaykitError` still catches it. What you must not do is raise a bare
`ValueError`, which escapes `except PaykitError` completely.
