- Storing ids in `Loan` (`self.isbn`, `self.member_id`) instead of the objects. Then the loan cannot ask
  its book for a title or its member for a name without going back to the library.
- `loans = []` as a class attribute of `Member`. Every member then shares one list of loans.
- Changing state before all checks: calling `book.lend()` or appending the loan and only then checking the
  limit. A refused checkout leaves a copy counted as lent.
- Hard-coding `14` and `2`. The tests change `Loan.PERIOD` and `Loan.FINE_PER_DAY`.
- `raise BookNotFound(isbn)` inside `except KeyError` without `from err`, or `from None`. The tests
  expect the `KeyError` as `__cause__`.
- Raising `KeyError`, `ValueError` or `IndexError` from library operations. Callers catch
  `LibraryError`; every operational problem must be one of its subclasses.
- Comparing days the wrong way. A book returned **on** the due day is on time; overdue means
  `day > due_day`.
- In `checkout_many`, stopping at the first failure or undoing the successful loans. The task keeps them
  and reports every failure in one group.
- Making `Library` a subclass of `dict`. Users could then call `library.clear()` and bypass every rule.
