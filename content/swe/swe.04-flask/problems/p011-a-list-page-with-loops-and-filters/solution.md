## Approach

```jinja
{% for post in posts %}
  <li class="post">
    <h2>{{ post.title|title }}</h2>
    <time>{{ post.created.strftime("%d %b %Y") }}</time>
    <p class="summary">{{ post.body|truncate(40) }}</p>
  </li>
{% else %}
  <li class="empty">No posts yet.</li>
{% endfor %}
```

The full file is `reference.py`: the dict `TEMPLATES` with this template, and the factory that sets `app.jinja_loader = jinja2.DictLoader(TEMPLATES)`.

Example: `LONG|truncate(40)` cuts at a word boundary near 40 characters and adds `...`: `Flask is a small framework that maps...`. A body of 45 characters or less (length plus a leeway of 5) is left untouched.

Jinja escapes `{{ ... }}` output by default (the template name ends in `.html`), so `<script>` in a title is shown as text. That default is your protection against XSS: the filters `title` and `truncate` keep it, and `|safe` would remove it.

## Complexity

`O(number of posts)`.

## Another way

Prepare the values in the view (format the date and cut the text in Python) and keep the template free of logic. Filters are the better place for pure presentation, and `{% else %}` saves an `if posts` test.

## Not covered

The real project has `templates/index.html` in a folder; the `DictLoader` only changes **where** the templates are read from.
