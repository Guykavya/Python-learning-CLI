- Raising the first error at once. The user then sees only one problem per try.
- Calling `ExceptionGroup("invalid user", [])` when everything is fine. An empty list raises
  `ValueError: second argument (exceptions) must be a non-empty sequence`.
- Adding the list itself as a single exception, or passing the errors as separate arguments:
  `ExceptionGroup("invalid user", *errors)`. The second argument is one list.
- Using separate `if`s for the age checks. A string age then gets a `TypeError` added and the range
  check crashes.
- Raising `ValueError("email")` for a missing key. Use `KeyError(field)` so callers can tell
  "missing" from "wrong".
- Writing `data.get("name", "")` and reporting "name must not be empty" for a missing name. Missing
  and empty are different problems.
