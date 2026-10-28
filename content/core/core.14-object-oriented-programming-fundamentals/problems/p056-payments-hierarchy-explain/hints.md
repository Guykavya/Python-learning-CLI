## Hint 1

Look at the caller's code. What decisions does it make? (Show a message to the customer, retry later,
or crash and let a developer look.) Each decision should become one class that a single `except`
clause can catch. The individual errors are subclasses inside those groups.

## Hint 2

Plan of the answer:

```text
1. PaykitError(Exception): catch "all paykit errors" without catching your own bugs
2. tree: ConfigurationError | InvalidRequest > InvalidCard, InvalidAmount, DuplicateCharge
         | CardDeclined | GatewayError > TemporaryGatewayError, UnexpectedResponse
3. attributes: decline_code, amount, order_id, retry_after, status/body
4. raise TemporaryGatewayError(...) from e  -> __cause__ keeps the low-level error
5. except: most specific first, PaykitError last
6. InvalidAmount(InvalidRequest, ValueError)? yes/no, and why
```
