## Approach

`create_autospec` inspects the class and builds a mock whose attributes and call signatures match it.
Methods are mocks too, so `return_value` can be set. The mock is therefore as strict as the real
class: a typo in the code under test is an error, not a silent pass. `transfer` is plain logic:
validate, withdraw, deposit only on success.

## Code

```python
from unittest.mock import create_autospec


def make_bank(bank_class):
    bank = create_autospec(bank_class, instance=True)
    bank.withdraw.return_value = True
    bank.balance.return_value = 100
    return bank


def transfer(bank, src, dst, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if bank.withdraw(src, amount):
        bank.deposit(dst, amount)
        return True
    return False
```

## Complexity

O(1).

## Another way

`Mock(spec=Bank)` also rejects unknown attributes but does **not** check call signatures;
`spec_set` also forbids setting new attributes. `autospec` is the strictest.
