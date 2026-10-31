class LibraryError(Exception):
    pass


# TODO: BookNotFound, MemberNotFound, BookUnavailable, LoanLimitReached, LoanNotFound, DuplicateError


class Book:
    def __init__(self, isbn, title, copies=1):
        # TODO
        pass


class Member:
    def __init__(self, member_id, name, limit=3):
        # TODO
        pass


class Loan:
    PERIOD = 14
    FINE_PER_DAY = 2

    def __init__(self, book, member, start_day):
        # TODO
        pass


class Library:
    def __init__(self, name):
        # TODO
        pass
