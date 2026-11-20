## Approach

```python
from django.template import Context, Template

COMMENT = Template('<p class="comment">{{ text|linebreaksbr }}</p>')


def render_comment(text):
    return COMMENT.render(Context({"text": text}))
```

- `{{ text }}` is auto-escaped: `<` becomes `&lt;`, `&` becomes `&amp;`, and so on. A browser shows the characters instead of running them, so `<script>` cannot run.
- `linebreaksbr` is applied to the **already escaped** value. It only adds the `<br>` tags that **you** produce, and Django marks the result as safe. That is why the order of escaping and adding tags matters: first escape, then add your own HTML.
- The visitor's text is a **value in the context**, never part of the template source. If you built `Template(text)` the visitor could write `{% ... %}` tags. The last test checks exactly this.
- The template is compiled once at import time and rendered many times: parsing is the slow part.

## Complexity

O(n) in the length of the text: one pass to escape, one to replace line breaks.

## Another way

In Python: `escape(text).replace("\n", "<br>")` with `django.utils.html.escape`, then `mark_safe` on the result if you want to put it into another template. It works, but the template version cannot be broken by forgetting the order. For URLs that should become links, the `urlize` filter also escapes the text first; this problem avoids it because user-written links need more care (`rel="nofollow"`, allowed schemes).
