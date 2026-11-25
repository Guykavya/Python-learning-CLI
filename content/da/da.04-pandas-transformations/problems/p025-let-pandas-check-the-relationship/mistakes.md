- **No `validate`.** The duplicated products silently duplicate their lines and every total goes up (fan-out, Ch. 6.8).
- **Letting `MergeError` escape.** It is a `ValueError`, but its message does not say which ids are duplicated.
- **Listing every id in the message, or one id several times.** The reader wants the short list of offenders.
- **`except Exception:`.** Catch the specific error; a bug elsewhere (a typo in a column name) must not be reported as
  "duplicated ids".
- **Dropping duplicates silently with `drop_duplicates("product_id")`.** Which of the two category rows is right is a
  business decision; the function should report, not guess.
