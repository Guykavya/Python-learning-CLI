class BankError(Exception):
    pass


class AccountNotFound(BankError):
    def __init__(self, account_id):
        self.account_id = account_id
        super().__init__(f"no account {account_id!r}")


class InsufficientFunds(BankError):
    def __init__(self, account_id, balance, amount):
        self.account_id = account_id
        self.balance = balance
        self.amount = amount
        super().__init__(f"account {account_id!r} has {balance}, needs {amount}")


class AccountFrozen(BankError):
    def __init__(self, account_id):
        self.account_id = account_id
        super().__init__(f"account {account_id!r} is frozen")


class TransferError(BankError):
    def __init__(self, source, target, amount):
        self.source = source
        self.target = target
        self.amount = amount
        super().__init__(f"transfer of {amount} from {source!r} to {target!r} failed")


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


class Account:
    def __init__(self, account_id, owner, balance=0):
        if not _is_int(balance) or balance < 0:
            raise ValueError("balance must be an int >= 0")
        self.account_id = account_id
        self.owner = owner
        self._balance = balance
        self.frozen = False

    @property
    def balance(self):
        return self._balance

    def freeze(self):
        self.frozen = True

    def _check(self, amount):
        if not _is_int(amount) or amount <= 0:
            raise ValueError("amount must be a positive int")
        if self.frozen:
            raise AccountFrozen(self.account_id)

    def deposit(self, amount):
        self._check(amount)
        self._balance += amount

    def withdraw(self, amount):
        self._check(amount)
        if amount > self._balance:
            raise InsufficientFunds(self.account_id, self._balance, amount)
        self._balance -= amount


class Bank:
    def __init__(self):
        self._accounts = {}
        self._log = []

    def open(self, account_id, owner, balance=0):
        if account_id in self._accounts:
            raise ValueError(f"account {account_id!r} already exists")
        account = Account(account_id, owner, balance)
        self._accounts[account_id] = account
        return account

    def get(self, account_id):
        try:
            return self._accounts[account_id]
        except KeyError:
            raise AccountNotFound(account_id) from None

    def transfer(self, source_id, target_id, amount):
        line = f"{amount} {source_id}->{target_id}"
        try:
            source = self.get(source_id)
            target = self.get(target_id)
            if source is target:
                raise ValueError("cannot transfer to the same account")
            source.withdraw(amount)
            try:
                target.deposit(amount)
            except BankError:
                source._balance += amount  # undo the withdrawal
                raise
        except (BankError, ValueError) as err:
            self._log.append(f"failed {line}: {err}")
            raise TransferError(source_id, target_id, amount) from err
        self._log.append(f"ok {line}")

    def statement(self):
        return list(self._log)
