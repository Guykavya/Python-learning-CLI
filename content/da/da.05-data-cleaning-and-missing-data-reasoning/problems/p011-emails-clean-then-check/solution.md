## Approach

Clean, then check, then keep. Cleaning turns `" ASHA@Mail.Example "` into a value the pattern can judge; the pattern
lists exactly which characters may appear where; `fullmatch` makes sure nothing else is left over; `where` keeps the
cleaned text only for the rows that passed. Rows that fail are not deleted: their email becomes missing, and the rest
of the row stays usable. The pattern is simple on purpose: a complete email regex is huge and still cannot tell whether
the mailbox exists.

## Code

```python
import pandas as pd


def clean_email(s):
    e = s.str.strip().str.lower()
    return e.where(e.str.fullmatch(r"[a-z0-9._+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+", na=False))
```

## Complexity

O(n) values, each checked once by a pattern that is linear in the text length.

## Another way

Keep the **uncleaned** lower-case text in a second column (`email_key`) for matching duplicates, as the chapter does in
section 5: a broken address like `meera1042mail.example` is still a perfectly good key for "the same respondent".
Another approach is `str.contains("@")` plus a few checks; it is easier to read but accepts many strings the pattern
rejects, so keep the one pattern and test it on a table of cases.
