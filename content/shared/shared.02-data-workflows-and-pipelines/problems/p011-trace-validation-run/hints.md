## Hint 1

Go record by record and keep three lists on paper: lines printed so far, `good`, and
`quarantine`. For each record ask: which `check` errors does it produce (in the order of
`REQUIRED`)? If none, which line of `transform` could fail, and with which exception class?
Is that class caught by `except (ValueError, KeyError)`? When are the `BAD` lines printed:
as they happen, or somewhere else?

## Hint 2

```
isinstance(True, int)            -> True   (bool is a subclass of int)
Decimal(" 4.25 ")                -> Decimal('4.25')   (spaces around are allowed)
Decimal("1e3")                   -> Decimal('1E+3')   (and that is how it prints)
Decimal("12,00")                 -> raises decimal.InvalidOperation, an ArithmeticError, NOT a ValueError
datetime.fromisoformat("...Z")   -> offset +00:00, so isoformat() ends in "+00:00"
fromisoformat("2024-06-03")      -> midnight, no offset: "2024-06-03T00:00:00"
fromisoformat("2024-02-30...")   -> ValueError (no 30 February)
finally runs on the way out, even after 'return' in the except block
```
