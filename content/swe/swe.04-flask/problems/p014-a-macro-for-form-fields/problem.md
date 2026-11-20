# A macro for form fields

Chapter section 7.2. Every form field repeats the same HTML: a label, an input that remembers its value, the error messages. A **macro** is a function for HTML. In `solution.py` the dict `TEMPLATES` holds two templates; write the macro `render_field` in `macros.html`:

```jinja
{% macro render_field(name, label, value="", errors=(), type="text") %} ... {% endmacro %}
```

What it must produce (the tests parse the HTML):

- `<label for="NAME">LABEL</label>`.
- `<input id="NAME" name="NAME" type="TYPE" value="VALUE">`. The value is **escaped** (a value with a quote must not break the attribute). For `type="password"` **never** print the value: a failed form must not send the password back to the browser.
- When `errors` is not empty:
  - the input also has `aria-invalid="true"` and `aria-describedby="NAME-errors"`;
  - after the input: `<ul class="errors" id="NAME-errors">` with one `<li>` per error (escaped).
- With no errors: none of the three (no `aria-invalid`, no `<ul>`).

`signup.html` (given in the starter) imports the macro; the view `/signup` already validates a POST and re-renders with `values` and `errors`. You only write the macro.

## Example

```text
render_field("email", "Email", "a@b.c", ["Not a valid address"])
<div class="field"><label for="email">Email</label>
<input id="email" name="email" type="text" value="a@b.c" aria-invalid="true" aria-describedby="email-errors">
<ul class="errors" id="email-errors"><li>Not a valid address</li></ul></div>
```
