# Template filling with re.sub

Web frameworks fill templates like `Hello {{ name }}, you owe {{ amount }}.` from a dict of
values. The core of such an engine is one `re.sub` call with a replacement **function** that
looks each name up.

Write `render(template: str, values: dict) -> str` in `solution.py`.

- A placeholder is `{{`, optional whitespace, a **name**, optional whitespace, `}}`.
  `{{name}}`, `{{ name }}` and `{{   name   }}` are all the same placeholder.
- A name is a Python-style identifier: a letter or `_`, then letters, digits or `_`.
- If the name is in `values`, the placeholder becomes `str(values[name])`.
- If it is **not** in `values`, the placeholder is left exactly as it was written (spaces included).
- Anything that is not a valid placeholder (`{ name }`, `{{ first name }}`, `{{ 1x }}`,
  `{{ user.name }}`) is plain text and stays.
- Values are inserted as they are: a value that contains `{{ x }}` or a backslash is **not**
  processed again.

**Example**

```python
render("Hello {{ name }}, you owe ₹{{amount}}.", {"name": "Kavya", "amount": 250})
# 'Hello Kavya, you owe ₹250.'
render("Dear {{ title }} {{ name }}", {"name": "Rao"})
# 'Dear {{ title }} Rao'
```
