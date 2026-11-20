## Hint 1

In which order do you want to treat the text: let the user's `<` stay, or neutralise it? What would happen to `<script>` if you first add your tags and then escape everything?

## Hint 2

`markupsafe.escape(text)` returns a `Markup` already; convert with `str(...)` before you do your own replacements, so that the final `Markup(...)` is the only place where you declare "this is safe". Use `re.sub` with `\*\*(.+?)\*\*`.

## Hint 3

```text
safe = str(escape(text))
safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
safe = safe.replace("\n", "<br>")
return Markup(safe)
```
