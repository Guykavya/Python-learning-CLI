## Approach

```jinja
{% macro render_field(name, label, value="", errors=(), type="text") -%}
<div class="field">
  <label for="{{ name }}">{{ label }}</label>
  <input id="{{ name }}" name="{{ name }}" type="{{ type }}"
    {%- if type != "password" %} value="{{ value or '' }}"{% endif %}
    {%- if errors %} aria-invalid="true" aria-describedby="{{ name }}-errors"{% endif %}>
  {%- if errors %}
  <ul class="errors" id="{{ name }}-errors">
    {%- for error in errors %}
    <li>{{ error }}</li>
    {%- endfor %}
  </ul>
  {%- endif %}
</div>
{%- endmacro %}
```

Example: for `render_field("email", "Email", "a@b.c", ["Not valid"])` the input gets `aria-invalid="true"` and `aria-describedby="email-errors"`, and the `<ul id="email-errors">` right after it is the text a screen reader reads for that field.

Each piece has a reason: `for`/`id` connect the label to the input (a click on the label focuses the field); `aria-invalid` and `aria-describedby` tell assistive technology that the field is wrong and why; the value is kept so the user does not retype everything; a password is never put back into HTML.

## Complexity

`O(number of errors)` per field.

## Another way

Flask-WTF/WTForms render fields for you, but you pay with a heavy form class. A 15-line macro is enough for many apps, and it is the same pattern those libraries use inside.

## Not covered

Textareas, selects and checkboxes need their own macros (or a `type` switch).
