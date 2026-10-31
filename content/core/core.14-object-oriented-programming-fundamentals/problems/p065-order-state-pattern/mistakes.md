- Keeping `self.status = "paid"` strings and `if self.status == ...` chains in `Order`. The new
  `Review` state in the tests then does not work.
- Changing `self._state` or the history **before** calling the state method. When the state raises,
  the order is left half-changed.
- Forgetting to pass the order: `self._state.cancel()` instead of `self._state.cancel(self)`. Then
  `Paid.cancel` cannot set `refunded`.
- A `can` that calls `self.cancel()` (the real action). It changes the state.
- A `can` that leaves `refunded = True` behind after the trial `Paid.cancel`.
- Storing state names in a class-level list `history = []`. Every order then shares one history.
