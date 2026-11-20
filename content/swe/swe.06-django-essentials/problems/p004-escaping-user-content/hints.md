## Hint 1

Where does the escaping happen in Django? Think about `{{ text }}` in a template: what does Django do with the value before it writes it? Which two ways would switch that protection off?

## Hint 2

The text must go into the template as a **variable** (in the context), not be part of the template source. `{{ text|linebreaksbr }}` escapes the text first, then turns each line break into `<br>`. Build the `Template` with the fixed HTML around the variable, and call `.render(Context({"text": text}))`.

## Hint 3

```text
TEMPLATE = Template('<p class="comment">{{ text|linebreaksbr }}</p>')
render_comment(text):
    return TEMPLATE.render(Context({"text": text}))
```
