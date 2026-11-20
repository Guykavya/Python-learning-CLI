## Approach

Escape the user's text, then add the few tags you allow, then mark the result safe.

```python
import re
from markupsafe import Markup, escape

BOLD = re.compile(r"\*\*(.+?)\*\*")


def format_comment(text):
    safe = str(escape(text))                              # 1. neutralise the user's HTML
    safe = BOLD.sub(r"<strong>\1</strong>", safe)         # 2. now add our own tags
    safe = safe.replace("\n", "<br>")
    return Markup(safe)                                   # 3. tell Jinja it is already safe
```

Example: `**<b>x</b>**`: after escaping it is `**&lt;b&gt;x&lt;/b&gt;**`; the regex only sees the stars, which escaping does not touch, and wraps the escaped text in `<strong>`. The only live tags in the output are the ones **your code** wrote.

`Markup` means "this string is already HTML-safe, do not escape it again". Use it only on text you have just escaped or built from constants.

## Complexity

`O(length of the text)`.

## Another way

Keep the user's text as plain text and let the template create the tags (split on `**` in Python and loop in Jinja). No `Markup` is needed, so nothing can go wrong. For richer formatting use a Markdown library followed by an HTML sanitiser with an allow-list (for example `bleach` or `nh3`): never write a full sanitiser by hand.

## Not covered

Links need care: `javascript:` URLs in `href`. This exercise only allows bold and line breaks.
