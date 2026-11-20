# A list page with loops and filters

Chapter sections 6.2 to 6.4. The runner does not copy `.html` files from your work folder, so in these problems **the templates live inside `solution.py`**, in a dict `TEMPLATES`, and the factory tells Flask to load from it:

```python
app.jinja_loader = jinja2.DictLoader(TEMPLATES)
```

(This is a convenience for the exercises. A real project uses a `templates/` folder, as in the chapter's project.)

`starter.py` already has the view and the factory. Your job is the template `index.html`. The view gives it a list `posts`; each post is a dict with `title`, `body` and `created` (a `datetime.date`). The page must show:

- An `<li class="post">` for every post, containing
  - `<h2>` with the title passed through the **`title`** filter (`hello WORLD of flask` becomes `Hello World Of Flask`),
  - `<time>` with the date written like `05 Mar 2026` (use `created.strftime("%d %b %Y")`),
  - `<p class="summary">` with the body passed through **`truncate(40)`**.
- When there are **no posts**: a single `<li class="empty">No posts yet.</li>` and no `post` items. Use the `{% else %}` branch of the `for` loop.
- Titles and bodies are user text: the autoescape of Jinja must stay on (no `|safe`).

## Example

```text
post: title "hello WORLD of flask", created 2026-03-05, body of 90 characters
-> <h2>Hello World Of Flask</h2> <time>05 Mar 2026</time> <p class="summary">Flask is a small framework that maps...</p>
```
