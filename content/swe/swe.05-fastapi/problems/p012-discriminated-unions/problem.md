# Discriminated unions

Chapter section 5.9 (discriminated unions), with 5.3 (`Field` patterns) and 5.8 (`loc` paths). A payment API accepts three kinds of payment in one endpoint. The field `method` tells which kind it is.

In `solution.py` define `app = FastAPI()` and:

```python
class PaymentBase(BaseModel):
    amount_paise: int = Field(gt=0)
```

and three models that **inherit** from it:

| Model | `method` | Other fields (all required, all `str` with `Field(pattern=...)`) |
|---|---|---|
| `Card` | `Literal["card"]` | `number`: 16 digits `^\d{16}$`; `expiry`: `MM/YY`, `^(0[1-9]\|1[0-2])/\d{2}$` |
| `Bank` | `Literal["bank"]` | `account`: 9 to 18 digits `^\d{9,18}$`; `ifsc`: `^[A-Z]{4}0[A-Z0-9]{6}$` |
| `Upi` | `Literal["upi"]` | `vpa`: `^[a-z0-9._-]+@[a-z]+$` (like `asha.k@okbank`) |

(In the table `\|` is a plain `|` in your pattern.) Then

```python
Payment = Annotated[Card | Bank | Upi, Field(discriminator="method")]
```

`POST /payments` takes `payment: Payment` as the body and returns, with status **201**:

```python
{"method": payment.method, "amount_paise": payment.amount_paise, "summary": <text>}
```

where the summary is `"card ending 1111"` (last 4 digits), `"bank HDFC0001234"` (the IFSC) or `"upi asha.k@okbank"` (the VPA).

What the discriminator buys you (the tests check it):

- A bad card is reported **only** against `Card`: one error at `["body", "card", "number"]`, not errors from `Bank` and `Upi` too.
- An unknown method gives **exactly one** error at `["body"]` with type `union_tag_invalid`.
- A body without `method` gives one error at `["body"]` with type `union_tag_not_found`.

## Example

```text
POST /payments {"method": "card", "amount_paise": 49900, "number": "4111111111111111", "expiry": "08/29"}
-> 201 {"method": "card", "amount_paise": 49900, "summary": "card ending 1111"}

POST /payments {"method": "card", "amount_paise": 100, "number": "4111", "expiry": "08/29"}
-> 422 [ {"loc": ["body", "card", "number"], "type": "string_pattern_mismatch", ...} ]

POST /payments {"method": "cash", "amount_paise": 100}
-> 422 [ {"loc": ["body"], "type": "union_tag_invalid", ...} ]
```
