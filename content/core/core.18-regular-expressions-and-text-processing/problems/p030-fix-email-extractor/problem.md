# Fix: the broken email extractor

`starter.py` holds `extract_emails`, written in a hurry for a college club's sign-up sheet. It
"works" on the one address it was tried with. Then the club secretary reports:

- "When a line has two addresses, I get one long string with both of them and everything in
  between."
- "`admin@localhost` and `test@site` show up as emails, but they have no dot in the domain."
- "People who typed their address in capitals, like `RAVI@GMAIL.COM`, are missing or cut short."
- "The address at the end of a sentence comes back with the full stop, sometimes."
- "`kavya%club@college.edu` comes back as `club@college.edu`."
- "`x@y.z` is accepted, but no real domain ends in a one-letter part."

Copy `starter.py` to `solution.py` and fix `extract_emails(text: str) -> list[str]`. Keep the
name and parameter. Fixing one symptom does **not** fix the others, so check each.

**What counts as an email** (find all of them, in order, spelled as written, duplicates kept):

- A **local part**: one or more of letters, digits, `.`, `_`, `%`, `+`, `-`.
- Then `@`.
- Then a **domain**: one or more labels made of letters, digits or `-`, **each followed by a
  dot**, and finally a top-level part of **2 or more letters** (`com`, `in`, `uk`).
  So `college.edu`, `mail.co.uk` and `my-site.in` are fine; `localhost` and `y.z` are not.
- Letters may be upper- or lower-case anywhere.
- The email ends at the last letter of the top-level part. A character that cannot belong to
  it (space, comma, `>`, a final `.`) is not part of it. If the top-level part runs straight
  into more letters or digits, as in `bob@site.com2`, it is not an email.

**Example**

```python
extract_emails("Mail kavya@example.com or ravi@club.co.in, thanks.")
# ['kavya@example.com', 'ravi@club.co.in']
extract_emails("Contact: <RAVI@GMAIL.COM>. Not: admin@localhost")
# ['RAVI@GMAIL.COM']
```
