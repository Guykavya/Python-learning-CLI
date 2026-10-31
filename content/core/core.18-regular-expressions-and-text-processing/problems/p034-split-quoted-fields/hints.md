## Hint 1

Describe **one field** as a pattern, then let `finditer` find all of them. A field is either
quoted or plain: which alternative must be tried first? What may appear inside the quotes?

## Hint 2

The hard part is not producing too many or too few empty fields. Anchor each field to what comes
before it and after it: it starts at the beginning of the line **or** right after a comma, and it
ends right before a comma **or** the end (a lookahead, so the comma is left for the next field).

```
FIELD = (?:^|,) \s* (?: "(?P<quoted>(?:[^"]|"")*)" | (?P<plain>[^,"]*?) ) \s* (?=,|$)

for m in finditer(FIELD, line):
    if m.group("quoted") is not None: add quoted with '""' replaced by '"'
    else: add m.group("plain")
```
