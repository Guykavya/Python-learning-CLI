## Hint 1

Write the rules as five separate `if` statements, not an `if/elif` chain. Why must a password such as `"aaa"` be able to appear in two problems at once?

## Hint 2

Two checks have a trap. `"" in "anything"` is `True` in Python: what does that do to the username rule when `username` is empty? And how do you tell "all characters are the same" without a loop? Think of a `set`.

## Hint 3

```text
problems = []
if len(pw) < 12: add "too_short"
if len(pw) > 256: add "too_long"
if pw.lower() in breached: add "breached"
if username and username.lower() in pw.lower(): add "contains_username"
if pw and len(set(pw)) == 1: add "one_character"
return problems
```
