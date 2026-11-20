# Stop the XSS

Chapter section 6.5. A comment page lets users write **a little formatting**: `**bold**` becomes bold text and a new line becomes a line break. The starter does it the dangerous way: its filter marks the whole comment as safe HTML, so a comment such as `<script>alert(1)</script>` runs in every visitor's browser.

In `solution.py` fix `format_comment(text)` so that it returns a `markupsafe.Markup` object that is **safe by construction**:

1. **Escape first** (`markupsafe.escape`): every `<`, `>`, `&` and quote of the user's text becomes harmless text.
2. **Then** turn `**word**` into `<strong>word</strong>` (the shortest match: `**a** and **b**` has two bold parts) and each `\n` into `<br>`.
3. Return the result as `Markup`, so the template does not escape it a second time.

The factory (already in the starter) registers it as the filter `comment_html` and shows `app.config["COMMENTS"]`, a list of `{"author": ..., "text": ...}`, on `GET /`. The author name is escaped by the normal autoescape.

The order matters: **escape, then add your own tags**. The reverse order lets the user's `<` break your tags (or smuggle theirs).

## Example

```python
format_comment("**hi** <b>x</b>\nbye")
# Markup('<strong>hi</strong> &lt;b&gt;x&lt;/b&gt;<br>bye')
```
