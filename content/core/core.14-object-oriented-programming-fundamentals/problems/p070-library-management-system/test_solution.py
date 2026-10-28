import pytest

from solution import (Book, BookNotFound, BookUnavailable, DuplicateError, Library, LibraryError, Loan,
                      LoanLimitReached, LoanNotFound, Member, MemberNotFound)


@pytest.fixture
def lib():
    lib = Library("City Library")
    lib.add_book(Book("978-81", "Dune", copies=2))
    lib.add_book(Book("978-93", "Gora"))
    lib.add_member(Member("M1", "Asha", limit=2))
    lib.add_member(Member("M2", "Ravi"))
    return lib


# ================================================================ exceptions

ERRORS = [
    (BookNotFound("978-81"), {"isbn": "978-81"}, "no book with ISBN 978-81"),
    (MemberNotFound("M9"), {"member_id": "M9"}, "no member with id M9"),
    (BookUnavailable("978-81"), {"isbn": "978-81"}, "no free copy of book 978-81"),
    (LoanLimitReached("M1", 3), {"member_id": "M1", "limit": 3}, "member M1 already has 3 loan(s)"),
    (LoanNotFound("M1", "978-81"), {"member_id": "M1", "isbn": "978-81"}, "member M1 has not borrowed book 978-81"),
    (DuplicateError("book", "978-81"), {"kind": "book", "key": "978-81"}, "book 978-81 already exists"),
]


@pytest.mark.parametrize("err, attrs, message", ERRORS, ids=lambda x: type(x).__name__ if isinstance(x, Exception) else "")
def test_exceptions(err, attrs, message):
    name = type(err).__name__
    assert isinstance(err, LibraryError), f"{name} must inherit from LibraryError so callers can catch every library error at once."
    for attr, value in attrs.items():
        assert getattr(err, attr, None) == value, f"{name} should store {attr}={value!r}."
    assert str(err) == message, f"str({name}(...)) should be {message!r}, got {str(err)!r}."


def test_library_error_is_an_exception():
    assert issubclass(LibraryError, Exception) and not issubclass(Exception, LibraryError), "LibraryError(Exception)."
    assert str(LibraryError("x")) == "x", "LibraryError keeps a plain message."


# ================================================================ Book

def test_book_basics():
    b = Book("978-81", "Dune", copies=2)
    assert (b.isbn, b.title, b.copies, b.on_loan, b.available) == ("978-81", "Dune", 2, 0, 2), "A new book: nothing on loan, all copies available."
    assert Book("1", "X").copies == 1, "copies defaults to 1."


@pytest.mark.parametrize("args, message", [
    (("", "Dune"), "isbn must be a non-empty string"),
    ((978, "Dune"), "isbn must be a non-empty string"),
    (("978", ""), "title must be a non-empty string"),
    (("978", None), "title must be a non-empty string"),
    (("978", "Dune", 0), "copies must be an int >= 1"),
    (("978", "Dune", 1.0), "copies must be an int >= 1"),
    (("978", "Dune", True), "copies must be an int >= 1"),
])
def test_book_validation(args, message):
    with pytest.raises(ValueError) as info:
        Book(*args)
    assert str(info.value) == message, f"Book{args} should raise ValueError({message!r}), got {str(info.value)!r}."


def test_book_lend_and_give_back():
    b = Book("978-81", "Dune", copies=2)
    b.lend()
    b.lend()
    assert (b.on_loan, b.available) == (2, 0), "Two copies lent: none available."
    with pytest.raises(BookUnavailable) as info:
        b.lend()
    assert info.value.isbn == "978-81" and b.on_loan == 2, "Never lend more copies than exist."
    b.give_back()
    assert b.available == 1, "give_back makes a copy available again."
    b.give_back()
    with pytest.raises(ValueError, match="no copy of this book is on loan"):
        b.give_back()
    assert b.on_loan == 0, "on_loan never goes below 0."


def test_available_is_read_only():
    b = Book("978-81", "Dune")
    with pytest.raises(AttributeError):
        b.available = 99
    assert isinstance(vars(Book).get("available"), property), "available is a property computed from copies - on_loan."


def test_book_repr():
    assert repr(Book("978-81", "Dune", copies=2)) == "Book('978-81', 'Dune', copies=2)", "repr format: Book('978-81', 'Dune', copies=2)."


# ================================================================ Member

def test_member_basics():
    m = Member("M1", "Asha")
    assert (m.member_id, m.name, m.limit, m.loans) == ("M1", "Asha", 3, []), "limit defaults to 3; loans starts empty."
    assert m.can_borrow() is True


def test_members_have_their_own_lists():
    a, b = Member("A", "a"), Member("B", "b")
    a.loans.append("x")
    assert b.loans == [], "Each member needs a new loans list (create it in __init__, not as a class attribute)."


@pytest.mark.parametrize("bad", [0, -1, 2.0, True, "3"])
def test_member_limit_validation(bad):
    with pytest.raises(ValueError, match="limit must be an int >= 1"):
        Member("M1", "Asha", limit=bad)


def test_member_repr():
    assert repr(Member("M1", "Asha", limit=2)) == "Member('M1', 'Asha', limit=2)", "repr format: Member('M1', 'Asha', limit=2)."


# ================================================================ Loan

def test_loan_basics():
    book, member = Book("978-81", "Dune"), Member("M1", "Asha")
    loan = Loan(book, member, 1)
    assert loan.book is book and loan.member is member, "A Loan stores the Book and Member OBJECTS, not their ids."
    assert (loan.start_day, loan.due_day) == (1, 15), "due_day = start_day + 14."
    assert repr(loan) == "Loan('978-81', 'M1', due=15)", "repr format: Loan('978-81', 'M1', due=15)."


def test_loan_class_attributes():
    assert (vars(Loan).get("PERIOD"), vars(Loan).get("FINE_PER_DAY")) == (14, 2), "Loan.PERIOD = 14 and Loan.FINE_PER_DAY = 2 are class attributes."


def test_loan_period_read_from_class(monkeypatch):
    monkeypatch.setattr(Loan, "PERIOD", 7)
    monkeypatch.setattr(Loan, "FINE_PER_DAY", 10)
    loan = Loan(Book("1", "X"), Member("M", "m"), 10)
    assert loan.due_day == 17, "Read the period through self.PERIOD (or type(self).PERIOD), not a hard-coded 14."
    assert loan.fine(20) == 30, "Read the fine rate through self.FINE_PER_DAY, not a hard-coded 2."


def test_overdue_and_fine():
    loan = Loan(Book("1", "X"), Member("M", "m"), 1)  # due 15
    assert [loan.is_overdue(d) for d in (14, 15, 16)] == [False, False, True], "Overdue only AFTER the due day: day > due_day."
    assert [loan.days_overdue(d) for d in (1, 15, 16, 25)] == [0, 0, 1, 10], "days_overdue is day - due_day, never below 0."
    assert [loan.fine(d) for d in (15, 16, 25)] == [0, 2, 20], "fine = days_overdue * 2."


# ================================================================ Library: books and members

def test_add_and_find(lib):
    book = Book("111", "New")
    assert lib.add_book(book) is book and lib.find_book("111") is book, "add_book returns the book; find_book finds the same object."
    m = Member("M3", "Cy")
    assert lib.add_member(m) is m and lib.find_member("M3") is m, "add_member returns the member; find_member finds it."
    assert lib.name == "City Library"


def test_duplicates(lib):
    with pytest.raises(DuplicateError, match="book 978-81 already exists") as info:
        lib.add_book(Book("978-81", "Other"))
    assert (info.value.kind, info.value.key) == ("book", "978-81")
    assert lib.find_book("978-81").title == "Dune", "A duplicate must not replace the existing book."
    with pytest.raises(DuplicateError, match="member M1 already exists"):
        lib.add_member(Member("M1", "Someone"))


def test_not_found_chained_from_key_error(lib):
    with pytest.raises(BookNotFound, match="no book with ISBN 000") as info:
        lib.find_book("000")
    assert isinstance(info.value.__cause__, KeyError), "Raise BookNotFound(isbn) from the KeyError of the dict lookup."
    with pytest.raises(MemberNotFound, match="no member with id M9") as info:
        lib.find_member("M9")
    assert isinstance(info.value.__cause__, KeyError), "Raise MemberNotFound(member_id) from the KeyError."


def test_internal_storage_not_a_dict_subclass():
    assert not isinstance(Library("x"), (dict, list)), "Library HAS books and members (composition); it is not a dict or list."


# ================================================================ checkout

def test_checkout(lib):
    loan = lib.checkout("M1", "978-81", day=1)
    assert isinstance(loan, Loan) and repr(loan) == "Loan('978-81', 'M1', due=15)", "checkout returns the new Loan."
    dune = lib.find_book("978-81")
    assert (dune.on_loan, dune.available) == (1, 1), "checkout lends one copy."
    assert lib.find_member("M1").loans == [loan], "The loan is added to the member's loans."
    assert loan.book is dune and loan.member is lib.find_member("M1"), "The loan points to the library's own Book and Member objects."


def test_checkout_unknown(lib):
    with pytest.raises(MemberNotFound):
        lib.checkout("M9", "978-81", day=1)
    with pytest.raises(BookNotFound):
        lib.checkout("M1", "000", day=1)
    assert lib.find_book("978-81").on_loan == 0 and lib.loans_of("M1") == [], "Failed checkouts change nothing."


def test_checkout_order_of_checks(lib):
    with pytest.raises(MemberNotFound):
        lib.checkout("M9", "000", day=1)  # member is checked before the book


def test_book_unavailable(lib):
    lib.checkout("M1", "978-93", day=1)
    with pytest.raises(BookUnavailable, match="no free copy of book 978-93"):
        lib.checkout("M2", "978-93", day=2)
    assert lib.loans_of("M2") == [], "A failed checkout does not add a loan."


def test_loan_limit(lib):
    lib.checkout("M1", "978-81", day=1)
    lib.checkout("M1", "978-93", day=1)
    with pytest.raises(LoanLimitReached, match="member M1 already has 2 loan\\(s\\)") as info:
        lib.checkout("M1", "978-81", day=2)
    assert (info.value.member_id, info.value.limit) == ("M1", 2)
    assert lib.find_book("978-81").on_loan == 1, (
        "Check everything first, change state last: a refused checkout must not lend a copy."
    )


def test_limit_checked_before_availability(lib):
    lib.checkout("M1", "978-93", day=1)
    lib.checkout("M1", "978-81", day=1)
    with pytest.raises(LoanLimitReached):
        lib.checkout("M1", "978-93", day=2)  # both rules are broken; the limit is checked first


def test_two_copies_same_member(lib):
    lib.checkout("M2", "978-81", day=1)
    lib.checkout("M2", "978-81", day=2)
    assert lib.find_book("978-81").available == 0, "A member may borrow two copies of the same book."


# ================================================================ return

def test_return_on_time(lib):
    lib.checkout("M1", "978-81", day=1)
    assert lib.return_book("M1", "978-81", day=15) == 0, "Returned on the due day: no fine."
    assert lib.find_book("978-81").available == 2 and lib.loans_of("M1") == [], "Return gives the copy back and removes the loan."
    assert lib.overdue(100) == [], "A returned loan is gone from the library's list too."


def test_return_late(lib):
    lib.checkout("M1", "978-81", day=1)
    assert lib.return_book("M1", "978-81", day=20) == 10, "5 days late * 2 = 10."


def test_return_oldest_loan_first(lib):
    lib.checkout("M2", "978-81", day=1)   # due 15
    lib.checkout("M2", "978-81", day=10)  # due 24
    assert lib.return_book("M2", "978-81", day=20) == 10, "With two loans of the same book, return the OLDEST one (due 15)."
    assert [loan.due_day for loan in lib.loans_of("M2")] == [24], "The newer loan stays."


def test_return_errors(lib):
    with pytest.raises(MemberNotFound):
        lib.return_book("M9", "978-81", day=1)
    with pytest.raises(LoanNotFound, match="member M1 has not borrowed book 978-81") as info:
        lib.return_book("M1", "978-81", day=1)
    assert (info.value.member_id, info.value.isbn) == ("M1", "978-81")
    lib.checkout("M2", "978-81", day=1)
    with pytest.raises(LoanNotFound):
        lib.return_book("M1", "978-81", day=2)  # Ravi has it, not Asha
    assert lib.find_book("978-81").on_loan == 1, "A failed return changes nothing."


def test_loans_of_is_a_copy(lib):
    lib.checkout("M1", "978-81", day=1)
    lib.loans_of("M1").clear()
    assert len(lib.loans_of("M1")) == 1, "loans_of returns a NEW list."
    with pytest.raises(MemberNotFound):
        lib.loans_of("M9")


# ================================================================ overdue

def test_overdue_list(lib):
    a = lib.checkout("M1", "978-81", day=1)   # due 15
    b = lib.checkout("M2", "978-81", day=3)   # due 17
    c = lib.checkout("M2", "978-93", day=10)  # due 24
    assert lib.overdue(15) == [], "Nothing is overdue on day 15."
    assert lib.overdue(16) == [a], "On day 16 only the first loan is overdue."
    assert lib.overdue(30) == [a, b, c], "overdue(day) keeps checkout order."


def test_overdue_report(lib):
    lib.checkout("M2", "978-93", day=10)  # due 24
    lib.checkout("M1", "978-81", day=1)   # due 15
    lib.checkout("M2", "978-81", day=3)   # due 17
    assert lib.overdue_report(20) == [
        "M1 Asha: 'Dune' due day 15, 5 day(s) late, fine 10",
        "M2 Ravi: 'Dune' due day 17, 3 day(s) late, fine 6",
    ], f"Got {lib.overdue_report(20)}. Only overdue loans, most days late first, in the exact format."
    assert lib.overdue_report(10) == [], "No overdue loans: an empty list."


def test_overdue_report_ties_keep_checkout_order(lib):
    lib.add_member(Member("M3", "Cy"))
    lib.checkout("M3", "978-81", day=5)
    lib.checkout("M1", "978-81", day=5)
    lib.checkout("M2", "978-93", day=1)
    report = lib.overdue_report(25)
    assert report == [
        "M2 Ravi: 'Gora' due day 15, 10 day(s) late, fine 20",
        "M3 Cy: 'Dune' due day 19, 6 day(s) late, fine 12",
        "M1 Asha: 'Dune' due day 19, 6 day(s) late, fine 12",
    ], f"Got {report}. Equal days late keep checkout order (sorted() is stable, also with reverse=True)."


# ================================================================ checkout_many

def test_checkout_many_success(lib):
    loans = lib.checkout_many("M2", ["978-81", "978-93"], day=1)
    assert [repr(loan) for loan in loans] == ["Loan('978-81', 'M2', due=15)", "Loan('978-93', 'M2', due=15)"], "Returns the new loans in order."


def test_checkout_many_collects_errors(lib):
    lib.checkout("M2", "978-93", day=1)
    with pytest.raises(ExceptionGroup) as info:
        lib.checkout_many("M1", ["978-81", "000", "978-93"], day=2)
    eg = info.value
    assert eg.message == "2 of 3 checkout(s) failed", f"Group message f'{{failed}} of {{total}} checkout(s) failed'. Got {eg.message!r}."
    assert [type(e).__name__ for e in eg.exceptions] == ["BookNotFound", "BookUnavailable"], "One error per failed ISBN, in order."
    assert [repr(loan) for loan in lib.loans_of("M1")] == ["Loan('978-81', 'M1', due=16)"], "Successful loans stay when others fail."


def test_checkout_many_limit(lib):
    with pytest.raises(ExceptionGroup) as info:
        lib.checkout_many("M1", ["978-81", "978-81", "978-93"], day=1)
    assert [type(e).__name__ for e in info.value.exceptions] == ["LoanLimitReached"], "Asha (limit 2) gets two loans; the third ISBN fails."
    assert len(lib.loans_of("M1")) == 2


def test_checkout_many_unknown_member(lib):
    with pytest.raises(MemberNotFound):
        lib.checkout_many("M9", ["978-81"], day=1)


def test_catch_everything_as_library_error(lib):
    for bad in (lambda: lib.find_book("x"), lambda: lib.checkout("M9", "978-81", 1),
                lambda: lib.return_book("M1", "978-81", 1), lambda: lib.add_member(Member("M1", "x"))):
        try:
            bad()
        except LibraryError:
            continue
        pytest.fail("Every library problem must raise a LibraryError subclass.")


def test_full_story(lib):
    lib.checkout("M1", "978-81", day=1)
    lib.checkout("M2", "978-81", day=3)
    with pytest.raises(BookUnavailable):
        lib.checkout("M2", "978-81", day=4)
    assert lib.return_book("M1", "978-81", day=20) == 10
    with pytest.raises(ExceptionGroup) as info:
        lib.checkout_many("M1", ["978-93", "000", "978-93"], day=21)
    assert [str(e) for e in info.value.exceptions] == ["no book with ISBN 000", "no free copy of book 978-93"]
    assert [repr(loan) for loan in lib.loans_of("M1")] == ["Loan('978-93', 'M1', due=35)"], "The example from problem.md."
