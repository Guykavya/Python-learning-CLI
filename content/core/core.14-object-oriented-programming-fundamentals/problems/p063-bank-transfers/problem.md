# Atomic bank transfers with chained errors

A transfer is two steps: take money out of one account, put it into another. If the second step fails,
the first must be **undone**, or money disappears. This "all or nothing" rule is called **atomic**.
Callers should also get **one** error type for "the transfer failed", with the real reason kept as its
cause.

All amounts are whole numbers (paise). In `solution.py` write:

### Exceptions

| class | parent | attributes | `str(e)` |
|---|---|---|---|
| `BankError` | `Exception` | | |
| `AccountNotFound` | `BankError` | `account_id` | `no account 'X'` |
| `InsufficientFunds` | `BankError` | `account_id`, `balance`, `amount` | `account 'A' has 50, needs 80` |
| `AccountFrozen` | `BankError` | `account_id` | `account 'A' is frozen` |
| `TransferError` | `BankError` | `source`, `target`, `amount` | `transfer of 80 from 'A' to 'B' failed` |

Each `__init__` takes the attributes in the order shown, stores them, and passes the message to
`super().__init__(message)`.

### `class Account`

- `Account(account_id, owner, balance=0)`. `balance` must be an `int >= 0` (not a `bool`), else
  `ValueError("balance must be an int >= 0")`.
- `balance` is a **read-only property** (no setter): store it in `self._balance`.
- `frozen` attribute, `False` at first; `freeze()` sets it to `True`.
- `deposit(amount)` and `withdraw(amount)`:
  - `amount` must be an `int > 0` (not a `bool`), else `ValueError("amount must be a positive int")`;
  - a frozen account raises `AccountFrozen`;
  - `withdraw` raises `InsufficientFunds` if `amount > balance`.
  - Checks happen in this order: amount, frozen, funds. A failed call changes nothing.

### `class Bank`

- `open(account_id, owner, balance=0)`: creates, stores and returns an `Account`. An id that already
  exists: `ValueError(f"account {account_id!r} already exists")`.
- `get(account_id)`: the account, or `AccountNotFound`. Look it up in a dict and turn the `KeyError`
  into `AccountNotFound(account_id)` with `raise ... from None` (the `KeyError` adds nothing).
- `transfer(source_id, target_id, amount)`:
  - if anything goes wrong, raise `TransferError(source_id, target_id, amount)` **from** the
    original exception (so `__cause__` is the `AccountNotFound`, `InsufficientFunds`,
    `AccountFrozen` or `ValueError`), and leave **both balances unchanged**;
  - transferring to the same account is an error too: the cause is
    `ValueError("cannot transfer to the same account")`;
  - order: look up both accounts, check same account, withdraw from the source, deposit into the
    target. If the deposit fails, put the money back into the source (undo), then raise.
- `statement()`: a new list of strings, one per `transfer` call, in order:
  - success: `"ok 80 A->B"`
  - failure: `"failed 80 A->B: <str of the cause>"`, for example
    `"failed 80 A->B: account 'A' has 50, needs 80"`.

## Example

```python
bank = Bank()
bank.open("A", "Asha", 100)
bank.open("B", "Ben")
bank.transfer("A", "B", 30)
bank.get("A").balance, bank.get("B").balance      # (70, 30)

bank.get("B").freeze()
bank.transfer("A", "B", 20)       # TransferError: transfer of 20 from 'A' to 'B' failed
                                  # __cause__: AccountFrozen: account 'B' is frozen
bank.get("A").balance             # 70   (the withdrawal was undone)

bank.statement()
# ['ok 30 A->B', "failed 20 A->B: account 'B' is frozen"]

bank.get("A").balance = 10**6     # AttributeError: read-only property
```
