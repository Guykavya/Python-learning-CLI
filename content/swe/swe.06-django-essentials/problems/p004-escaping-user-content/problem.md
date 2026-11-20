# Escaping user content

Chapter sections 5.1 and 5.2. Visitors write comments, and your page shows them. Whatever a visitor types is **data**, never HTML. Django's templates escape every variable by default; your job is to keep that protection and still show line breaks.

In `solution.py` write `render_comment(text)`. It must use a Django `Template` and return a string:

```text
<p class="comment">TEXT</p>
```

where `TEXT` is the comment with

1. every special HTML character escaped (`<`, `>`, `&`, `'`, `"`), and
2. every line break turned into `<br>` (use the `linebreaksbr` filter).

Do **not** use `|safe`, `mark_safe` or `urlize`: a URL in a comment stays plain (escaped) text, not a link.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). This problem has no models, so you only write the function. Django's template settings are already configured, so `Template("...")` from `django.template` works.

## Example

```text
render_comment("Hi <b>there</b>")  ->  <p class="comment">Hi &lt;b&gt;there&lt;/b&gt;</p>
render_comment("one\ntwo")         ->  <p class="comment">one<br>two</p>
```

The starter pastes the text straight into the HTML: this is exactly how an XSS hole is made. The tests show which attacks get through.
