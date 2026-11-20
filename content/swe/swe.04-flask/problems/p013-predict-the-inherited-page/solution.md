## Approach

Resolve each block from the most specific template to the least.

```text
--- base.html
[base head]
[base content]
[base footer: demo]
--- page.html
[page head] [base head]
[page content for Asha]
[base footer: demo]
--- special.html
[page head] [base head]
[special] [page content for Asha]
DEMO
```

- **base.html.** Its blocks show their default text; `{{ site }}` is `demo`.
- **page.html.** `head` is replaced by `[page head] ` plus `super()`, which is the base's head. `content` is replaced (no `super()`), using `name`. `footer` is not overridden, so the base's footer shows.
- **special.html.** It inherits `head` from `page.html` (so the text is the same as in `page.html`). `content` is `[special] ` plus `super()`: the parent here is `page.html`, so you get `[page content for Asha]`, **not** the base's text. `footer` becomes `{{ site|upper }}`, which is `DEMO`.

The context (`site`, `name`) is shared by the whole chain: the child templates do not need to mention a variable for its block in the parent to use it.

Real output of the program, run with Jinja2 3.1.6.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Print `env.get_template("special.html").blocks.keys()` to see which blocks a template defines itself.

## Not covered

A `{% block %}` inside a `{% for %}` cannot see the loop variable unless it is marked `scoped`.
