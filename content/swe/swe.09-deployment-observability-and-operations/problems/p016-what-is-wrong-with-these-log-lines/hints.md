## Hint 1

For each line ask four questions: Could it leak something private? Could a machine search it (fixed message, named fields)? Does it carry a level and the request id? How many records does it produce, and how big are they?

## Hint 2

The fix for most lines has the same shape: a short constant message and the facts as fields, through the logger, for example `log.info("order created", extra={"fields": {"order_id": order.id}})`. The exceptions are (a) and (b), where the right fix is to log **less**, and (d), where the right fix is **one** call to `log.exception`.
