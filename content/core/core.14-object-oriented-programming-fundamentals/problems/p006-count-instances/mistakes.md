- Writing `self.count += 1`. It creates an instance attribute on the new ticket; the class counter
  stays 0 and every number is 1.
- Setting `count = 0` inside `__init__`. That resets the counter for every new ticket.
- Not storing `self.number`, and reading `Ticket.count` later instead. Then every old ticket "changes
  number" when a new one is made.
- Forgetting `@classmethod`. `Ticket.reset()` then fails with "missing 1 required positional argument".
- Writing `self.count = 0` in `reset`. A classmethod has `cls`, not `self`; and through an instance it
  would only hide the class counter.
