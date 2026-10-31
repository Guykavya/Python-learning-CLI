## Approach

The design follows chapter section 20.

- **Four classes, each guarding its own rules.** `Book` never lends more copies than it has (and
  `available` is a read-only property, so nobody can set it). `Member` knows its limit. `Loan` computes
  its due day once and knows its own overdue and fine rules, reading `PERIOD` and `FINE_PER_DAY` from the
  class. `Library` only coordinates: it finds objects and calls their methods.
- **Composition everywhere** (section 14): the library *has* dicts and a list in `_` attributes; a loan
  *refers to* a book and a member object. Nothing inherits except the exceptions.
- **One exception hierarchy** (section 17): `LibraryError` at the top, specific subclasses with the
  data a caller needs. Lookups translate `KeyError` with `raise ... from err` (section 18).
- **Check first, change last:** every method raises before it changes anything, so a failed call leaves
  the library exactly as it was.
- **Exception group** (section 19): `checkout_many` reports every failed ISBN at once.

## Code

```python
# ---------------------------------------------------------------- exceptions

class LibraryError(Exception):
    """Base class for every error raised by the library system."""


class BookNotFound(LibraryError):
    def __init__(self, isbn):
        self.isbn = isbn
        super().__init__(f"no book with ISBN {isbn}")


class MemberNotFound(LibraryError):
    def __init__(self, member_id):
        self.member_id = member_id
        super().__init__(f"no member with id {member_id}")


class BookUnavailable(LibraryError):
    def __init__(self, isbn):
        self.isbn = isbn
        super().__init__(f"no free copy of book {isbn}")


class LoanLimitReached(LibraryError):
    def __init__(self, member_id, limit):
        self.member_id = member_id
        self.limit = limit
        super().__init__(f"member {member_id} already has {limit} loan(s)")


class LoanNotFound(LibraryError):
    def __init__(self, member_id, isbn):
        self.member_id = member_id
        self.isbn = isbn
        super().__init__(f"member {member_id} has not borrowed book {isbn}")


class DuplicateError(LibraryError):
    def __init__(self, kind, key):
        self.kind = kind
        self.key = key
        super().__init__(f"{kind} {key} already exists")


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _is_text(x):
    return isinstance(x, str) and x != ""


# ---------------------------------------------------------------- domain classes

class Book:
    def __init__(self, isbn, title, copies=1):
        if not _is_text(isbn):
            raise ValueError("isbn must be a non-empty string")
        if not _is_text(title):
            raise ValueError("title must be a non-empty string")
        if not _is_int(copies) or copies < 1:
            raise ValueError("copies must be an int >= 1")
        self.isbn = isbn
        self.title = title
        self.copies = copies
        self.on_loan = 0

    @property
    def available(self):
        return self.copies - self.on_loan

    def lend(self):
        if self.available == 0:
            raise BookUnavailable(self.isbn)
        self.on_loan += 1

    def give_back(self):
        if self.on_loan == 0:
            raise ValueError("no copy of this book is on loan")
        self.on_loan -= 1

    def __repr__(self):
        return f"Book({self.isbn!r}, {self.title!r}, copies={self.copies})"


class Member:
    def __init__(self, member_id, name, limit=3):
        if not _is_int(limit) or limit < 1:
            raise ValueError("limit must be an int >= 1")
        self.member_id = member_id
        self.name = name
        self.limit = limit
        self.loans = []

    def can_borrow(self):
        return len(self.loans) < self.limit

    def __repr__(self):
        return f"Member({self.member_id!r}, {self.name!r}, limit={self.limit})"


class Loan:
    PERIOD = 14
    FINE_PER_DAY = 2

    def __init__(self, book, member, start_day):
        self.book = book
        self.member = member
        self.start_day = start_day
        self.due_day = start_day + self.PERIOD

    def is_overdue(self, day):
        return day > self.due_day

    def days_overdue(self, day):
        return max(0, day - self.due_day)

    def fine(self, day):
        return self.days_overdue(day) * self.FINE_PER_DAY

    def __repr__(self):
        return f"Loan({self.book.isbn!r}, {self.member.member_id!r}, due={self.due_day})"


# ---------------------------------------------------------------- the library

class Library:
    def __init__(self, name):
        self.name = name
        self._books = {}
        self._members = {}
        self._loans = []

    def add_book(self, book):
        if book.isbn in self._books:
            raise DuplicateError("book", book.isbn)
        self._books[book.isbn] = book
        return book

    def add_member(self, member):
        if member.member_id in self._members:
            raise DuplicateError("member", member.member_id)
        self._members[member.member_id] = member
        return member

    def find_book(self, isbn):
        try:
            return self._books[isbn]
        except KeyError as err:
            raise BookNotFound(isbn) from err

    def find_member(self, member_id):
        try:
            return self._members[member_id]
        except KeyError as err:
            raise MemberNotFound(member_id) from err

    def checkout(self, member_id, isbn, day):
        member = self.find_member(member_id)
        book = self.find_book(isbn)
        if not member.can_borrow():
            raise LoanLimitReached(member_id, member.limit)
        if book.available == 0:
            raise BookUnavailable(isbn)
        loan = Loan(book, member, day)
        book.lend()
        member.loans.append(loan)
        self._loans.append(loan)
        return loan

    def return_book(self, member_id, isbn, day):
        member = self.find_member(member_id)
        for loan in member.loans:
            if loan.book.isbn == isbn:
                break
        else:
            raise LoanNotFound(member_id, isbn)
        fine = loan.fine(day)
        member.loans.remove(loan)
        self._loans.remove(loan)
        loan.book.give_back()
        return fine

    def loans_of(self, member_id):
        return list(self.find_member(member_id).loans)

    def overdue(self, day):
        return [loan for loan in self._loans if loan.is_overdue(day)]

    def overdue_report(self, day):
        late = sorted(self.overdue(day), key=lambda loan: loan.days_overdue(day), reverse=True)
        return [
            f"{loan.member.member_id} {loan.member.name}: {loan.book.title!r} due day {loan.due_day}, "
            f"{loan.days_overdue(day)} day(s) late, fine {loan.fine(day)}"
            for loan in late
        ]

    def checkout_many(self, member_id, isbns, day):
        self.find_member(member_id)
        loans = []
        errors = []
        for isbn in isbns:
            try:
                loans.append(self.checkout(member_id, isbn, day))
            except LibraryError as err:
                errors.append(err)
        if errors:
            raise ExceptionGroup(f"{len(errors)} of {len(isbns)} checkout(s) failed", errors)
        return loans
```

Notes:

- `sorted(..., reverse=True)` is still **stable**: loans with the same days late keep checkout order.
- `self.PERIOD` finds the class attribute (instances have no own `PERIOD`), so
  `Loan.PERIOD = 7` changes all new loans. Do not write `14` into `__init__`.
- `for ... else` in `return_book`: the `else` runs only when the loop did not `break`, i.e. no loan
  matched.

## Complexity

`find_book`, `find_member`, `checkout` and `add_*` are O(1) on average (dict lookups). `return_book`
is O(k + L) for a member with k loans and L loans in the library (`list.remove`). `overdue` is O(L) and
`overdue_report` O(L log L) because of the sort.

## Another way

Keep loans in a dict keyed by `(member_id, isbn)` with a list of loans as value, so `return_book` is
O(1). Or give the library a list of "events" (checkout, return) and compute everything from it, which
also gives a full history. For the extensions: a `ReferenceBook(Book)` can override `lend()` to raise
`BookUnavailable` always; inheritance is fine there because a reference book really **is** a book and
keeps every promise except lending, which `Book` already allows to fail.
