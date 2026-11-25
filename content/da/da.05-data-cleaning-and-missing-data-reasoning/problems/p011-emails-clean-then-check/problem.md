# Emails: clean, then check

Chapter section 4.3. Raw emails have upper case (`MEERA1002@MAIL.EXAMPLE`), spaces around them, and sometimes lost their
`@`. The order matters: **clean first, then check**. The check is deliberately simple: "looks like an email, so it can
be used as a key". (Only sending a message can prove that an address exists.)

Write `clean_email(s)`. `s` is a Series of text (values may be missing). Return a Series with the same index:

1. Strip spaces at both ends and make the text lower case.
2. Keep it if the **whole** cleaned text matches this pattern, otherwise the result is **missing**:
   - a local part of one or more of: lower-case letters, digits, `.`, `_`, `+`, `-`
   - then one `@`
   - then a domain: one or more of lower-case letters, digits, `-`, followed by **one or more** groups of a dot and
     one or more of those same characters (so at least one dot is needed)
3. A missing input gives a missing output. No error is ever raised.

In regex form: `[a-z0-9._+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+`.

## Cases

| input | output |
|---|---|
| `Asha@Example.COM ` | `asha@example.com` |
| `dev.k+x@sub.mail.example` | same |
| `user_name@mail.example` | same |
| `MEERA1002@MAIL.EXAMPLE` | `meera1002@mail.example` |
| `meera1042mail.example` (no `@`) | missing |
| `a@b` (no dot in the domain) | missing |
| `a@x..com`, `a@x.com.` (empty part) | missing |
| `@x.com` (empty local part) | missing |
| `a@@x.com`, `a@b@x.com` (two `@`) | missing |
| `a b@x.com` (space inside) | missing |
| `a@x.com extra` | missing |
| empty text | missing |

## Example

```python
import pandas as pd

print(clean_email(pd.Series(["Asha@Example.COM ", " meera1042mail.example", "a@b", None, "dev.k+x@sub.mail.example"])).tolist())
```

```text
['asha@example.com', nan, nan, nan, 'dev.k+x@sub.mail.example']
```
