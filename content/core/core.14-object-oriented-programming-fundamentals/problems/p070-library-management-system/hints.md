## Hint 1

Do not write `Library` first. Write the six exception classes (each is four lines), then `Book`, and
run the tests: the `Book` tests pass on their own. Then `Member`, then `Loan`. Which of these classes
needs a property, which needs a class attribute, and which must create a **new list** in `__init__`?

## Hint 2

In `Library`, two private helpers do most of the work: `find_book` and `find_member`, each a dict
lookup in a `try` that turns `KeyError` into your own exception **from** the `KeyError`.

`checkout` is a list of checks that may raise, followed by the changes. Why must every check come
before `book.lend()` and the two `append` calls?

For `return_book`, `for ... else` finds the first matching loan or raises in the `else`.

## Hint 3

```text
checkout(member_id, isbn, day):
    member = find_member(member_id); book = find_book(isbn)
    if not member.can_borrow(): raise LoanLimitReached(member_id, member.limit)
    if book.available == 0:     raise BookUnavailable(isbn)
    loan = Loan(book, member, day); book.lend()
    member.loans.append(loan); self._loans.append(loan); return loan

overdue_report(day):
    late = sorted(overdue(day), key=days_overdue(day), reverse=True)    # stable
    return [f"{id} {name}: {title!r} due day {due}, {days} day(s) late, fine {fine}" for each]

checkout_many(member_id, isbns, day):
    find_member(member_id)
    loans, errors = [], []
    for isbn in isbns:
        try: loans.append(checkout(member_id, isbn, day))
        except LibraryError as err: errors.append(err)
    if errors: raise ExceptionGroup(f"{len(errors)} of {len(isbns)} checkout(s) failed", errors)
    return loans
```
