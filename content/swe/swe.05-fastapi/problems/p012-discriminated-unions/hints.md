## Hint 1

The starter already accepts good payments. Send it `{"method": "cash", "amount_paise": 100}` in your head: a plain union tries `Card`, then `Bank`, then `Upi`, and each fails in its own way. How many errors is that? What does section 5.9 add so that Pydantic looks at `method` first and tries **one** model only?

## Hint 2

The discriminator goes on the union with `Annotated[..., Field(discriminator="method")]`. Each member must declare `method` as a `Literal` with its own value (they already do). For the summary, check which class the object is with `isinstance`, or compare `payment.method`.

## Hint 3

```text
Payment = Annotated[Card | Bank | Upi, Field(discriminator="method")]

def summary(p):
    Card -> "card ending " + p.number[-4:]
    Bank -> "bank " + p.ifsc
    Upi  -> "upi " + p.vpa

POST /payments (status 201) -> {"method", "amount_paise", "summary": summary(payment)}
```
