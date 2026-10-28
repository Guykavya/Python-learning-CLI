- Forgetting `super().__init__(owner, balance)` in a subclass. Then `self.transactions` does not
  exist and the first `deposit` crashes with `AttributeError`.
- Writing `Account.__init__(self, owner, balance)` instead. It works here, but it breaks in
  multiple inheritance; `super()` is the normal way.
- In `Account.withdraw`, comparing with `self.balance` instead of `self.available()`. Then the
  overridden `available()` in `CheckingAccount` is never used.
- Counting the withdrawal **before** calling `super().withdraw`. A failed withdrawal then uses up
  one of the three.
- Forgetting to reset the count in `add_interest`.
- Copying `deposit` into every subclass. Inherited methods do not need to be written again.
- Creating `transactions = []` in the class body. All accounts would share one list.
