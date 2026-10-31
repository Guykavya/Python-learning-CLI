## Hint 1

Read the starter pattern one piece at a time and say in words what each piece accepts:
`[\w.+-]+`, `@`, `.+`, `.`, `[a-z]+`. Which piece can cross a space? Which piece matches any
character although it looks like a full stop? Which characters from the rules are missing from
a class?

## Hint 2

Rebuild the domain from the rules instead of patching: a label is `[A-Za-z0-9-]+`, each label
is followed by an escaped dot, and there is at least one label: `(?:[A-Za-z0-9-]+\.)+`. Then the
top-level part: letters, at least two. What stops `bob@site.com2` from matching `bob@site.co`?

## Hint 3

```
local  = [\w.%+-]+
domain = (?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}
EMAIL_RE = compile(local + "@" + domain + r"\b")
return EMAIL_RE.findall(text)
```
