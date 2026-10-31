# Project: a library management system

This is the build project of the module. Chapter section 20 walks through the design; here is the
exact interface the tests expect. You model a real domain with four classes that work together by
**composition**, and a **custom exception hierarchy** that callers can catch as a whole or one by one.

Days are plain integers (day 1, day 2, ...). "Today" is always passed in as an argument called `day`,
so nothing depends on the real clock and the tests are deterministic.

Build it in this order, running the tests as you go: exceptions, `Book`, `Member`, `Loan`, `Library`.

## 1. Exceptions

| class | parent | `__init__` arguments = attributes | `str(e)` |
|---|---|---|---|
| `LibraryError` | `Exception` | (message) | the message |
| `BookNotFound` | `LibraryError` | `isbn` | `no book with ISBN 978-81` |
| `MemberNotFound` | `LibraryError` | `member_id` | `no member with id M9` |
| `BookUnavailable` | `LibraryError` | `isbn` | `no free copy of book 978-81` |
| `LoanLimitReached` | `LibraryError` | `member_id`, `limit` | `member M1 already has 3 loan(s)` |
| `LoanNotFound` | `LibraryError` | `member_id`, `isbn` | `member M1 has not borrowed book 978-81` |
| `DuplicateError` | `LibraryError` | `kind`, `key` | `book 978-81 already exists` (`kind` is `"book"` or `"member"`) |

Each subclass stores its attributes and passes the message to `super().__init__(message)`.

## 2. `Book`

- `Book(isbn, title, copies=1)`.
  - `isbn` and `title` must be non-empty strings: else `ValueError("isbn must be a non-empty string")` /
    `ValueError("title must be a non-empty string")`.
  - `copies` must be an `int >= 1` (not a `bool`): else `ValueError("copies must be an int >= 1")`.
- Attribute `on_loan`, starting at `0`.
- `available`: a **read-only property**, `copies - on_loan`.
- `lend()`: if no copy is available raise `BookUnavailable(isbn)`; else `on_loan += 1`.
- `give_back()`: if `on_loan == 0` raise `ValueError("no copy of this book is on loan")`; else `on_loan -= 1`.
- `repr(book)` is `Book('978-81', 'Dune', copies=2)`.

## 3. `Member`

- `Member(member_id, name, limit=3)`. `limit` must be an `int >= 1` (not a `bool`), else
  `ValueError("limit must be an int >= 1")`.
- Attribute `loans`: a list of this member's current `Loan` objects (a new list per member).
- `can_borrow()`: `True` while `len(loans) < limit`.
- `repr(member)` is `Member('M1', 'Asha', limit=3)`.

## 4. `Loan`

- Class attributes `PERIOD = 14` (days) and `FINE_PER_DAY = 2` (rupees). Read them through `self`
  (or `type(self)`), so that changing `Loan.PERIOD` changes the period of **new** loans.
- `Loan(book, member, start_day)`: stores the **objects** `book` and `member`, `start_day`, and computes
  `due_day = start_day + PERIOD` once.
- `is_overdue(day)`: `day > due_day`.
- `days_overdue(day)`: `day - due_day`, but never below `0`.
- `fine(day)`: `days_overdue(day) * FINE_PER_DAY`.
- `repr(loan)` is `Loan('978-81', 'M1', due=15)` (the book's ISBN, the member's id).

## 5. `Library`

The library **has** books (a dict by ISBN), members (a dict by id) and the current loans (a list in
checkout order). Keep them in `_` attributes and offer methods.

- `Library(name)`: attribute `name`.
- `add_book(book)` / `add_member(member)`: store and return it. Same ISBN / id again:
  `DuplicateError("book", isbn)` / `DuplicateError("member", member_id)`.
- `find_book(isbn)` / `find_member(member_id)`: return the object. Unknown: `BookNotFound(isbn)` /
  `MemberNotFound(member_id)`, raised **from the `KeyError`** of the dict lookup (so `__cause__` is that
  `KeyError`).
- `checkout(member_id, isbn, day)` -> the new `Loan`. Check in this order, **change nothing until all
  checks passed**:
  1. find the member (`MemberNotFound`); 2. find the book (`BookNotFound`);
  3. `LoanLimitReached(member_id, member.limit)` if the member cannot borrow;
  4. `BookUnavailable(isbn)` if no copy is free.
  Then create the loan, call `book.lend()`, and add the loan to the member's list and the library's list.
  A member may borrow two copies of the same book.
- `return_book(member_id, isbn, day)` -> the fine (an `int`, `0` if on time). Find the member
  (`MemberNotFound`), then the member's **oldest** current loan of that ISBN; none: `LoanNotFound(member_id, isbn)`.
  Compute the fine, remove the loan from both lists, call `book.give_back()`.
- `loans_of(member_id)`: a **new** list with the member's current loans, oldest first (`MemberNotFound`
  for an unknown id).
- `overdue(day)`: a list of the current loans that are overdue on `day`, in checkout order.
- `overdue_report(day)`: one string per overdue loan:

  ```text
  M2 Ravi: 'Dune' due day 15, 5 day(s) late, fine 10
  ```

  (`f"{member_id} {name}: {title!r} due day {due_day}, {days} day(s) late, fine {fine}"`), sorted by
  days late, **most late first**; equal days keep checkout order.
- `checkout_many(member_id, isbns, day)` -> list of the new loans. Find the member first (an unknown
  member raises `MemberNotFound` directly). Then try `checkout` for each ISBN in order. A `LibraryError`
  for one ISBN does not stop the others; the successful loans **stay**. If any failed, raise
  `ExceptionGroup(f"{failed} of {total} checkout(s) failed", errors)` with the errors in order;
  otherwise return the loans.

## Example

```python
lib = Library("City Library")
dune = lib.add_book(Book("978-81", "Dune", copies=2))
lib.add_book(Book("978-93", "Gora"))
asha = lib.add_member(Member("M1", "Asha", limit=2))
lib.add_member(Member("M2", "Ravi"))

loan = lib.checkout("M1", "978-81", day=1)
loan                         # Loan('978-81', 'M1', due=15)
dune.available               # 1
lib.checkout("M2", "978-81", day=3)
lib.checkout("M2", "978-81", day=4)   # BookUnavailable: no free copy of book 978-81

lib.overdue_report(20)
# ["M1 Asha: 'Dune' due day 15, 5 day(s) late, fine 10",
#  "M2 Ravi: 'Dune' due day 17, 3 day(s) late, fine 6"]

lib.return_book("M1", "978-81", day=20)   # 10
lib.return_book("M1", "978-81", day=20)   # LoanNotFound: member M1 has not borrowed book 978-81

try:
    lib.find_book("000")
except LibraryError as err:               # one except catches every library problem
    print(err, type(err.__cause__).__name__)   # no book with ISBN 000 KeyError

lib.checkout_many("M1", ["978-93", "000", "978-93"], day=21)
# ExceptionGroup: 2 of 3 checkout(s) failed
#   BookNotFound: no book with ISBN 000
#   BookUnavailable: no free copy of book 978-93     ('Gora' has one copy, and Asha just took it)
lib.loans_of("M1")           # [Loan('978-93', 'M1', due=35)]   the successful loan stays
```

## Ideas to go further (not tested)

A `ReferenceBook(Book)` that can never be lent; members with different limits and loan periods
(`StudentMember`, `FacultyMember`) and a `Loan` that asks the member for its period; saving and loading
the library as JSON (core.11); a `check_all()` that reports every broken rule in one `ExceptionGroup`.
