## Hint 1

A macro is declared with `{% macro name(arguments) %} ... {% endmacro %}` and its output is the text between the tags. What changes in the output between "no errors" and "some errors"? Which parts always stay?

## Hint 2

Use `{% if errors %}` twice: once inside the `<input ...>` tag for the two `aria-*` attributes, once after it for the `<ul>`. The password rule is another `{% if type != "password" %}` around the `value="..."` attribute. Values and errors are escaped automatically in `{{ }}`.

## Hint 3

```text
<div class="field">
  <label for="NAME">LABEL</label>
  <input id=NAME name=NAME type=TYPE [value=VALUE unless password] [aria-invalid, aria-describedby if errors]>
  [<ul class="errors" id="NAME-errors"> <li>each error</li> </ul>  if errors]
</div>
```
