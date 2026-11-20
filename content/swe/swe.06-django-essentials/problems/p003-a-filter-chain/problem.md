# A filter chain

Chapter sections 5.1 and 5.2, and "Try it: a filter chain". Filters work from left to right: each one receives the result of the one before it. Below, six small templates are rendered with the same context. The program prints each result inside square brackets, so you can see spaces and empty results.

Write what the program prints. Some facts you need and may not remember:

- `truncatechars:8` makes the text **at most 8 characters long, counting the ellipsis** (a single character `…`, written in your answer exactly like that).
- `date:"Y-m-d"` writes year-month-day with a four-digit year and two-digit month and day.
- A variable that does not exist renders as an empty string (no error), unless you turn that on in the settings.

```python
import datetime

import django
from django.conf import settings

settings.configure(TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates"}])
django.setup()

from django.template import Context, Template

context = Context({
    "count": 0,
    "title": "hello world",
    "when": datetime.date(2026, 3, 9),
    "items": ["a", "b", "c"],
    "bold": "<b>hi</b>",
})
sources = [
    '{{ count|default:"none" }}',
    "{{ title|upper|truncatechars:8 }}",
    '{{ when|date:"Y-m-d" }}',
    "{{ items|length }} items",
    "{{ missing }}",
    "{{ bold }} {{ bold|safe }}",
]
for number, source in enumerate(sources, 1):
    print(f"{number}: [{Template(source).render(context)}]")
```

Write your answer in `answer.txt`: six lines, `1: [...]` to `6: [...]`, in the format of the `print` above. In line 6 write the escaped text as Django produces it (HTML entities). Do not run it.

## After you answer

1. Line 1: `count` is `0`, not missing. Why does `default` still replace it? What would you use to replace only a missing value (look at `default_if_none`)?
2. Line 2: what happens if you swap the order, `truncatechars:8|upper`? Is the result different?
3. Line 6: the two outputs come from the same variable. Which one is safe to use with text a user typed, and which one gives an attacker a way to run a script?
