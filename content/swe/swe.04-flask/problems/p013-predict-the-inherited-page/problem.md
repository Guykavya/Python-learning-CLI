# Predict the inherited page

Chapter sections 7.1 and 7.4. Three templates form a chain: `special.html` extends `page.html`, which extends `base.html`. The `-` signs in `{%- ... -%}` remove the whitespace around a tag, so the output has **no blank lines** and every line below is exactly what you must write.

```python
from jinja2 import DictLoader, Environment

TEMPLATES = {
    "base.html": """\
{%- block head -%}
[base head]
{%- endblock %}
{% block content -%}
[base content]
{%- endblock %}
{% block footer -%}
[base footer: {{ site }}]
{%- endblock %}
""",
    "page.html": """\
{%- extends "base.html" -%}
{%- block head -%}
[page head] {{ super() }}
{%- endblock -%}
{%- block content -%}
[page content for {{ name }}]
{%- endblock -%}
""",
    "special.html": """\
{%- extends "page.html" -%}
{%- block content -%}
[special] {{ super() }}
{%- endblock -%}
{%- block footer -%}
{{ site|upper }}
{%- endblock -%}
""",
}
env = Environment(loader=DictLoader(TEMPLATES))
for name in ("base.html", "page.html", "special.html"):
    out = env.get_template(name).render(site="demo", name="Asha")
    print(f"--- {name}")
    print(out)
```

Write in `answer.txt` everything the program prints: for each template a line `--- <name>` followed by the three lines of its rendered page. Do not run it. (Flask uses the same Jinja2 engine; section 7.1 explains `extends`, `block` and `super()`.)

## After you answer

1. Which blocks does `special.html` change, and which does it inherit from `page.html`?
2. What does `super()` give inside `special.html`'s `content` block: the text of `base.html`, or of `page.html`?
3. `{{ name }}` is used in `page.html`'s block, but `special.html` never mentions it. Why does it still work?
